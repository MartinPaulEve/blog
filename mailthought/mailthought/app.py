"""The Flask webhook receiver.

POST /inbound is the Mailgun route target. The request is vetted
(signature, replay, sender, SPF/DKIM), classified, and persisted to
the inbox on disk *before* the 200 goes back — an accepted email must
survive a crash. The actual work happens on a single background worker
so concurrent emails cannot interleave git operations or builds.
Rejections are 406 (Mailgun: permanent failure, do not retry) and are
never answered by email; the reason goes to the app log only.
"""

import json
import logging
import os
import queue
import shutil
import threading
import time
import uuid
from pathlib import Path

from flask import Flask, request

from . import extract, publisher, security
from .config import Config, load_config

logger = logging.getLogger(__name__)

# Webhook tokens only need to outlive the signature tolerance window;
# Message-Ids guard against slow route retries and keep the week.
TOKEN_TTL_SECONDS = 3600
MESSAGE_TTL_SECONDS = 7 * 86400


class HealthzLogFilter(logging.Filter):
    """Drops /healthz access-log lines: Coolify pings the endpoint
    constantly and the noise buries the deliveries worth reading."""

    def filter(self, record):
        return "/healthz" not in record.getMessage()


def persist_job(
    inbox_dir: Path,
    kind: str,
    sender: str,
    message_id: str,
    subject: str,
    text: str,
    images: list,
    draft_id: str | None = None,
    needs_auth: bool = False,
) -> dict:
    """Write a job durably to the inbox; returns the job dict.

    Image bytes become files beside job.json so the queue survives a
    restart; the returned dict is what job.json holds (image entries
    carry paths, not bytes).
    """
    job_id = uuid.uuid4().hex
    job_dir = Path(inbox_dir) / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    for seq, image in enumerate(images, 1):
        path = job_dir / f"image-{seq}"
        path.write_bytes(image["data"])
        entries.append(
            {
                "path": str(path),
                "mime": image["mime"],
                "alt": image.get("alt", ""),
                "filename": image.get("filename", ""),
            }
        )
    job = {
        "id": job_id,
        "kind": kind,
        "draft_id": draft_id,
        "sender": sender,
        "message_id": message_id,
        "subject": subject,
        "text": text,
        "images": entries,
        "dir": str(job_dir),
        "needs_auth": needs_auth,
    }
    (job_dir / "job.json").write_text(
        json.dumps(job, ensure_ascii=False), encoding="utf-8"
    )
    return job


def load_pending_jobs(inbox_dir: Path) -> list:
    """Jobs left in the inbox by an earlier run (crash recovery)."""
    inbox_dir = Path(inbox_dir)
    if not inbox_dir.is_dir():
        return []
    jobs = []
    for directory in sorted(inbox_dir.iterdir()):
        job_file = directory / "job.json"
        if job_file.is_file():
            jobs.append(json.loads(job_file.read_text(encoding="utf-8")))
    return jobs


def clear_job(job: dict) -> None:
    """Remove a completed job's directory (idempotent)."""
    directory = job.get("dir")
    if directory:
        shutil.rmtree(directory, ignore_errors=True)


def start_worker(config: Config, process=publisher.process_job):
    """A daemon thread draining a queue of jobs, one at a time.

    Returns (enqueue, thread). Pending jobs from a previous run are
    re-queued ahead of new arrivals. ``process`` is injectable so
    tests can observe ordering without running the pipeline.
    """
    jobs: queue.Queue = queue.Queue()
    pending = load_pending_jobs(config.inbox_dir)
    if pending:
        logger.info(
            "re-queueing %d job(s) left over from a previous run",
            len(pending),
        )
    for job in pending:
        jobs.put(job)

    def drain():
        while True:
            job = jobs.get()
            logger.info(
                "worker: starting job %s (kind=%s, %d image(s), from=%r)",
                job.get("id"), job.get("kind"),
                len(job.get("images") or []), job.get("sender"),
            )
            started = time.monotonic()
            try:
                process(job, config)
                logger.info(
                    "worker: job %s finished in %.1fs",
                    job.get("id"), time.monotonic() - started,
                )
            except Exception:  # one bad job must not stop the queue
                logger.exception(
                    "worker: job %s failed after %.1fs",
                    job.get("id"), time.monotonic() - started,
                )
            finally:
                clear_job(job)
                jobs.task_done()

    thread = threading.Thread(target=drain, daemon=True, name="mailthought-worker")
    thread.start()
    return jobs.put, thread


def create_app(
    config: Config | None = None,
    enqueue=None,
    fetch_mime=None,
    verify_dkim=None,
) -> Flask:
    """Build the Flask app; config defaults to the environment.

    ``enqueue`` is called with each accepted job dict; when omitted, a
    real worker thread is started. ``fetch_mime`` and ``verify_dkim``
    are the direct-DKIM fallback used when Mailgun's SPF/DKIM verdict
    headers are absent (large messages skip its spam scan); they
    default to the real Mailgun-storage fetch and dkimpy verification
    and are injectable for tests.
    """
    config = config or load_config(os.environ)
    # Mailgun abandons the webhook POST after ~10s ("context deadline
    # exceeded"), so the in-request fetch gets one short-timeout try;
    # anything slower is the worker's business via needs_auth.
    fetch_mime = fetch_mime or (
        lambda config, message_id: security.stored_message_mime(
            config, message_id, attempts=1, timeout=5.0
        )
    )
    verify_dkim = verify_dkim or security.dkim_authenticated
    for directory in (config.inbox_dir, config.state_dir, config.drafts_dir):
        directory.mkdir(parents=True, exist_ok=True)
    if enqueue is None:
        enqueue, _thread = start_worker(config)

    tokens = security.SeenLedger(
        config.state_dir / "tokens.json", ttl_seconds=TOKEN_TTL_SECONDS
    )
    messages = security.SeenLedger(
        config.state_dir / "messages.json", ttl_seconds=MESSAGE_TTL_SECONDS
    )

    # INFO-level logging throughout, so successful deliveries leave a
    # trail too, not only rejections. basicConfig is a no-op when a
    # handler already exists; the format matches Flask's own.
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    )
    access_log = logging.getLogger("gunicorn.access")
    if not any(
        isinstance(existing, HealthzLogFilter)
        for existing in access_log.filters
    ):
        access_log.addFilter(HealthzLogFilter())
    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)

    @app.post("/inbound")
    def inbound():
        form = request.form
        sender = security.sender_address(form.get("from", ""))
        subject = form.get("subject", "")
        message_id = extract.header_value(
            form.get("message-headers"), "Message-Id"
        ) or form.get("Message-Id", "")
        app.logger.info(
            "inbound POST: from=%r subject=%r message_id=%r bytes=%s "
            "attachments=%s",
            sender, subject, message_id, request.content_length,
            [
                f"{request.files[name].filename} "
                f"({request.files[name].mimetype})"
                for name in sorted(request.files)
            ] or "none",
        )

        def reject(reason, detail):
            app.logger.warning(
                "inbound rejected (%s): %s [from=%r subject=%r "
                "message_id=%r]",
                reason, detail, sender, subject, message_id,
            )
            return {"status": "rejected", "reason": reason}, 406

        if not security.verify_signature(
            config.mailgun_signing_key,
            form.get("timestamp", ""),
            form.get("token", ""),
            form.get("signature", ""),
        ):
            return reject(
                "signature",
                "timestamp=%r server_now=%d"
                % (form.get("timestamp", ""), time.time()),
            )
        if tokens.seen_before(form.get("token", "")):
            return reject("replay", "token=%r" % form.get("token", "")[:8])
        if not security.sender_allowed(
            form.get("from", ""), config.allowed_senders
        ):
            return reject("sender", "from=%r" % sender)
        app.logger.info(
            "signature verified, sender %r allowed", sender
        )

        verdicts = security.auth_results(form.get("message-headers", ""))
        app.logger.info(
            "Mailgun auth verdicts: spf=%r dkim=%r",
            verdicts["spf"], verdicts["dkim"],
        )
        needs_auth = False
        if config.require_auth and not security.is_authenticated(verdicts):
            if verdicts["spf"] or verdicts["dkim"]:
                return reject(
                    "authentication",
                    "spf=%r dkim=%r" % (verdicts["spf"], verdicts["dkim"]),
                )
            # Both verdicts absent: Mailgun's spam scan (which stamps
            # them) skips messages over its size limit — typically mail
            # with image attachments — so verify DKIM ourselves against
            # the stored copy of the message.
            app.logger.info(
                "verdict headers absent (message likely exceeded "
                "Mailgun's spam-scan size limit); falling back to "
                "direct DKIM verification of the stored message"
            )
            if not message_id:
                return reject(
                    "authentication",
                    "verdicts absent and no Message-Id to retrieve the "
                    "stored message by",
                )
            raw_mime = fetch_mime(config, message_id)
            if raw_mime is None:
                # The Events API has not indexed the message yet, and
                # Mailgun's ~10s webhook deadline leaves no room to
                # wait — accept provisionally; the worker verifies
                # DKIM before anything publishes.
                app.logger.info(
                    "stored message %r not queryable yet; deferring "
                    "DKIM verification to the worker", message_id,
                )
                needs_auth = True
            else:
                from_domain = sender.rsplit("@", 1)[-1]
                if not verify_dkim(raw_mime, from_domain):
                    return reject(
                        "authentication",
                        f"direct DKIM verification failed for domain "
                        f"{from_domain!r} ({len(raw_mime)} bytes of "
                        f"stored MIME)",
                    )
                app.logger.info(
                    "authenticated via direct DKIM verification for %r "
                    "(%d bytes of stored MIME)",
                    from_domain, len(raw_mime),
                )

        if message_id and messages.seen_before(message_id):
            app.logger.info(
                "duplicate delivery of %r acknowledged without "
                "re-queueing", message_id,
            )
            return {"status": "duplicate"}, 200

        body = extract.select_body(form)
        action = extract.classify(subject, body)
        images = extract.collect_images(
            request.files, form.get("content-id-map")
        )
        job = persist_job(
            config.inbox_dir,
            kind=action.kind,
            sender=sender,
            message_id=message_id,
            subject=subject,
            text=body,
            images=images,
            draft_id=action.draft_id,
            needs_auth=needs_auth,
        )
        enqueue(job)
        app.logger.info(
            "queued job %s: kind=%s draft_id=%r text=%d chars, "
            "%d image(s) kept%s",
            job["id"], action.kind, action.draft_id, len(body), len(images),
            " (pending DKIM verification)" if needs_auth else "",
        )
        return {"status": "queued", "id": job["id"]}, 200

    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    return app
