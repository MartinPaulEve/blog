"""The Flask webhook receiver.

POST /inbound is the Mailgun route target. The request is vetted
(signature, replay, sender, SPF/DKIM), classified, and persisted to
the inbox on disk *before* the 200 goes back — an accepted email must
survive a crash. The actual work happens on a single background worker
so concurrent emails cannot interleave git operations or builds.
Rejections are 406 (Mailgun: permanent failure, do not retry) and are
never answered by email.
"""

import json
import os
import queue
import shutil
import threading
import traceback
import uuid
from pathlib import Path

from flask import Flask, request

from . import extract, publisher, security
from .config import Config, load_config

# Webhook tokens only need to outlive the signature tolerance window;
# Message-Ids guard against slow route retries and keep the week.
TOKEN_TTL_SECONDS = 3600
MESSAGE_TTL_SECONDS = 7 * 86400


def persist_job(
    inbox_dir: Path,
    kind: str,
    sender: str,
    message_id: str,
    subject: str,
    text: str,
    images: list,
    draft_id: str | None = None,
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
    for job in load_pending_jobs(config.inbox_dir):
        jobs.put(job)

    def drain():
        while True:
            job = jobs.get()
            try:
                process(job, config)
            except Exception:  # noqa: BLE001 — one bad job must not stop the queue
                traceback.print_exc()
            finally:
                clear_job(job)
                jobs.task_done()

    thread = threading.Thread(target=drain, daemon=True, name="mailthought-worker")
    thread.start()
    return jobs.put, thread


def create_app(config: Config | None = None, enqueue=None) -> Flask:
    """Build the Flask app; config defaults to the environment.

    ``enqueue`` is called with each accepted job dict; when omitted, a
    real worker thread is started.
    """
    config = config or load_config(os.environ)
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

    app = Flask(__name__)

    @app.post("/inbound")
    def inbound():
        form = request.form
        if not security.verify_signature(
            config.mailgun_signing_key,
            form.get("timestamp", ""),
            form.get("token", ""),
            form.get("signature", ""),
        ):
            return {"status": "rejected", "reason": "signature"}, 406
        if tokens.seen_before(form.get("token", "")):
            return {"status": "rejected", "reason": "replay"}, 406
        if not security.sender_allowed(
            form.get("from", ""), config.allowed_senders
        ):
            return {"status": "rejected", "reason": "sender"}, 406
        if config.require_auth and not security.is_authenticated(
            security.auth_results(form.get("message-headers", ""))
        ):
            return {"status": "rejected", "reason": "authentication"}, 406

        message_id = extract.header_value(
            form.get("message-headers"), "Message-Id"
        ) or form.get("Message-Id", "")
        if message_id and messages.seen_before(message_id):
            return {"status": "duplicate"}, 200

        body = extract.select_body(form)
        action = extract.classify(form.get("subject", ""), body)
        images = extract.collect_images(
            request.files, form.get("content-id-map")
        )
        job = persist_job(
            config.inbox_dir,
            kind=action.kind,
            sender=security.sender_address(form.get("from", "")),
            message_id=message_id,
            subject=form.get("subject", ""),
            text=body,
            images=images,
            draft_id=action.draft_id,
        )
        enqueue(job)
        return {"status": "queued", "id": job["id"]}, 200

    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    return app
