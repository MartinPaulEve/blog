"""Driving the existing thought pipeline from a job.

The gateway deliberately reimplements nothing: storing, threading,
image constraints, Bluesky/Mastodon posting and the build+rsync deploy
all happen inside `uv run --project thought_composer thought …` in the
blog checkout, exactly as ./thought.sh does locally. What the CLI does
not do is git — the checkout here is ephemeral to Martin's machine, so
every published thought is committed and pushed back to GitHub, and
pulled freshly before each job (his machine pushes too).

Every function takes an injectable ``run`` callable (subprocess.run
shaped, evedeploy style) so the whole pipeline is unit-testable
without touching git, uv or the network.
"""

import logging
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from . import drafts, mailer, security

logger = logging.getLogger(__name__)

COMMIT_MESSAGE = "chore(thoughts): add {thought_id} via mail gateway"

# Polling budget for deferred DKIM verification: the worker can afford
# to wait out the Events API's ingestion lag (unlike the webhook,
# which Mailgun abandons after ~10s).
VERIFY_FETCH_ATTEMPTS = 31  # ~5 minutes at 10s spacing
VERIFY_FETCH_DELAY = 10.0

THOUGHT_BASE = [
    "uv", "run", "--env-file", ".env",
    "--project", "thought_composer", "thought",
]

# The CLI's success line: "(N post(s))" historically, "(N Bluesky
# post(s), M Mastodon)" since the per-service split. Group 2 is the
# (Bluesky) post count either way.
STORED_RE = re.compile(
    r"^Stored thought (\d+) \((\d+) (?:Bluesky )?post\(s\)(?:, \d+ Mastodon)?\)\."
)
# The CLI prints plain "--- post N ---" markers when Bluesky and
# Mastodon split identically, service-labelled ones when they differ.
POST_MARKER_RE = re.compile(r"^--- ((?:Bluesky |Mastodon )?post \d+) ---$")

IMAGE_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}


@dataclass
class PublishResult:
    ok: bool
    thought_id: str | None = None
    posts: int = 0
    bluesky: str | None = None
    mastodon: str | None = None
    warnings: list = field(default_factory=list)
    error: str | None = None
    pushed: bool = False


@dataclass
class DryRunResult:
    status: str
    posts: list = field(default_factory=list)
    labels: list = field(default_factory=list)


def default_run(cmd, cwd=None, check=True):
    """Run a command capturing text output; the only real-system touchpoint."""
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)


def thought_command(
    text: str,
    image_paths=(),
    alts=(),
    dry_run: bool = False,
) -> list:
    """The argv vector for the thought CLI, mirroring thought.sh.

    Email content rides only in argument values — never through a
    shell — so nothing in a thought can become a command. An --alt is
    emitted for every --image (empty when unknown) because the CLI
    pairs them positionally.
    """
    cmd = THOUGHT_BASE + ["--text", text]
    alts = list(alts) + [""] * (len(list(image_paths)) - len(list(alts)))
    for path in image_paths:
        cmd += ["--image", str(path)]
    for alt in alts[: len(list(image_paths))]:
        cmd += ["--alt", alt]
    if dry_run:
        cmd.append("--dry-run")
    return cmd


def parse_dry_run_output(stdout: str) -> DryRunResult:
    """The status line and per-post segments from `thought --dry-run`.

    ``labels`` carries each segment's marker text ("post 1" or
    "Bluesky post 1"), parallel to ``posts``.
    """
    lines = (stdout or "").splitlines()
    status = lines[0].strip() if lines else ""
    posts, labels = [], []
    current = None
    for line in lines[1:]:
        marker = POST_MARKER_RE.match(line.strip())
        if marker:
            if current is not None:
                posts.append("\n".join(current).strip("\n"))
            labels.append(marker.group(1))
            current = []
        elif current is not None:
            current.append(line)
    if current is not None:
        posts.append("\n".join(current).strip("\n"))
    return DryRunResult(status=status, posts=posts, labels=labels)


def parse_publish_output(stdout: str) -> PublishResult:
    """What actually happened, from the CLI's output.

    "Stored thought <id> (<n> post(s))." marks success; Bluesky:/
    Mastodon: lines carry the syndication URLs (only URL-shaped values
    count — "Bluesky: no password set; skipped." is a warning);
    WARNING lines are collected verbatim. One service failing is a
    partial success, as in the CLI itself.
    """
    result = PublishResult(ok=False)
    for raw in (stdout or "").splitlines():
        line = raw.strip()
        stored = STORED_RE.match(line)
        if stored:
            result.ok = True
            result.thought_id = stored.group(1)
            result.posts = int(stored.group(2))
        elif line.startswith("Bluesky: "):
            value = line[len("Bluesky: "):]
            if value.startswith("http"):
                result.bluesky = value
            else:
                result.warnings.append(line)
        elif line.startswith("Mastodon: "):
            value = line[len("Mastodon: "):]
            if value.startswith("http"):
                result.mastodon = value
            else:
                result.warnings.append(line)
        elif line.startswith("WARNING"):
            result.warnings.append(line)
    if not result.ok:
        result.error = (stdout or "").strip()
    return result


def dry_run(blog_dir: Path, text: str, run=default_run) -> DryRunResult:
    """Preview the thread split without touching anything."""
    completed = run(
        thought_command(text, dry_run=True), cwd=blog_dir, check=False
    )
    return parse_dry_run_output(completed.stdout or "")


def publish(
    blog_dir: Path,
    text: str,
    images: list,
    run=default_run,
    workdir: Path | None = None,
) -> PublishResult:
    """Publish a thought end to end; returns what happened.

    git pull --rebase → write attachment bytes to files → thought CLI
    (stores, syndicates, builds, rsyncs) → git add/commit/push (one
    pull --rebase retry on a rejected push). A deploy or push failure
    after the thought stored is reported as a warning on a successful
    result, matching the CLI's own semantics.
    """
    blog_dir = Path(blog_dir)
    warnings = []

    pulled = run(["git", "pull", "--rebase"], cwd=blog_dir, check=False)
    if pulled.returncode != 0:
        warnings.append("WARNING: git pull --rebase failed before publishing.")

    if workdir is not None:
        Path(workdir).mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=workdir) as staging:
        paths, alts = [], []
        for seq, image in enumerate(images, 1):
            extension = IMAGE_EXTENSIONS.get(image["mime"], ".bin")
            path = Path(staging) / f"attachment-{seq}{extension}"
            path.write_bytes(image["data"])
            paths.append(str(path))
            alts.append(image.get("alt", ""))
        completed = run(
            thought_command(text, paths, alts), cwd=blog_dir, check=False
        )

    result = parse_publish_output(completed.stdout or "")
    result.warnings = warnings + result.warnings
    if not result.ok:
        detail = ((completed.stdout or "") + (completed.stderr or "")).strip()
        result.error = detail or "thought CLI failed with no output"
        return result
    if completed.returncode != 0:
        result.warnings.append(
            "WARNING: the quick deploy failed; the thought is stored and "
            "will reach the site with the next deploy."
        )

    add_paths = ["_data/thoughts.yml"] + (["assets/thoughts"] if images else [])
    run(["git", "add", "-A", "--", *add_paths], cwd=blog_dir, check=False)
    staged = run(["git", "diff", "--cached", "--quiet"], cwd=blog_dir, check=False)
    if staged.returncode != 0:  # non-zero: something is staged
        run(
            ["git", "commit", "-m",
             COMMIT_MESSAGE.format(thought_id=result.thought_id)],
            cwd=blog_dir, check=False,
        )
        pushed = run(["git", "push"], cwd=blog_dir, check=False)
        if pushed.returncode != 0:
            run(["git", "pull", "--rebase"], cwd=blog_dir, check=False)
            pushed = run(["git", "push"], cwd=blog_dir, check=False)
        result.pushed = pushed.returncode == 0
        if not result.pushed:
            result.warnings.append(
                "WARNING: git push failed; the thought is live but not yet "
                "back in the repository."
            )
    return result


def process_job(
    job: dict,
    config,
    run=default_run,
    send=None,
    fetch_mime=None,
    verify_dkim=None,
) -> None:
    """Execute one persisted inbox job and mail the outcome back.

    ``job`` is the dict app.py persisted before returning 200:
    {"kind", "sender", "message_id", "subject", "text", "draft_id",
    "images": [{"path", "mime", "alt", "filename"}], "needs_auth"}.
    A needs_auth job was accepted before DKIM could be checked (the
    webhook could not retrieve the stored message within Mailgun's
    deadline) and must pass direct DKIM verification here before any
    of the pipeline runs. ``send`` is mailer.send_email-shaped;
    ``fetch_mime``/``verify_dkim`` are security-function-shaped — all
    injectable for tests.
    """
    send = send or mailer.send_email
    to = job["sender"]
    in_reply_to = job.get("message_id") or None

    def reply(pair):
        subject, body = pair
        delivered = send(config, to, subject, body, in_reply_to=in_reply_to)
        logger.info(
            "reply %r to %r %s",
            subject, to, "sent" if delivered else "FAILED to send",
        )

    if job.get("needs_auth"):
        fetch = fetch_mime or _fetch_stored_mime
        verify = verify_dkim or security.dkim_authenticated
        raw_mime = fetch(config, job.get("message_id") or "")
        if raw_mime is None:
            logger.error(
                "job %s: stored message %r never became retrievable "
                "from Mailgun; dropping the job and notifying the "
                "sender", job.get("id"), job.get("message_id"),
            )
            reply(mailer.failure_notice(
                "The original email could not be retrieved from "
                "Mailgun to verify its authenticity. (Large messages "
                "skip Mailgun's own SPF/DKIM checks, so the gateway "
                "re-checks them against Mailgun's stored copy of the "
                "message.)"
            ))
            return
        from_domain = to.rsplit("@", 1)[-1]
        if not verify(raw_mime, from_domain):
            logger.warning(
                "job %s: deferred DKIM verification failed for %r "
                "(%d bytes of stored MIME); dropping silently",
                job.get("id"), from_domain, len(raw_mime),
            )
            return
        logger.info(
            "job %s: deferred DKIM verification passed for %r",
            job.get("id"), from_domain,
        )

    def log_outcome(result):
        if result.ok:
            logger.info(
                "published thought %s (%d post(s), bluesky=%s, "
                "mastodon=%s, pushed=%s)",
                result.thought_id, result.posts,
                result.bluesky or "no", result.mastodon or "no",
                result.pushed,
            )
            for warning in result.warnings:
                logger.warning("publish warning: %s", warning)
        else:
            logger.error("publish failed: %s", result.error)

    kind = job.get("kind")

    if kind == "bad_reply":
        logger.info(
            "job %s: reply about draft %r had no POST first line",
            job.get("id"), job.get("draft_id"),
        )
        reply(mailer.bad_reply_notice(job.get("draft_id") or "unknown"))
        return

    if kind == "dry_run":
        images = _job_images(job)
        result = dry_run(config.blog_dir, job.get("text", ""), run=run)
        drafts.prune_drafts(config.drafts_dir)
        draft_id = drafts.new_draft_id()
        drafts.save_draft(
            config.drafts_dir, draft_id,
            text=job.get("text", ""), images=images,
            sender=to, message_id=job.get("message_id", ""),
        )
        logger.info(
            "job %s: dry run saved as draft %s (%d post(s), %d image(s))",
            job.get("id"), draft_id, len(result.posts), len(images),
        )
        reply(mailer.dry_run_report(draft_id, result, image_count=len(images)))
        return

    if kind == "post_draft":
        draft_id = job.get("draft_id") or ""
        draft = drafts.load_draft(config.drafts_dir, draft_id)
        if draft is None:
            logger.warning(
                "job %s: draft %r not found (expired or already "
                "published)", job.get("id"), draft_id,
            )
            reply(mailer.missing_draft_notice(draft_id))
            return
        result = publish(config.blog_dir, draft["text"], draft["images"], run=run)
        log_outcome(result)
        if result.ok:
            drafts.delete_draft(config.drafts_dir, draft_id)
            reply(mailer.receipt(result))
        else:
            reply(mailer.failure_notice(result.error or "unknown failure"))
        return

    images = _job_images(job)
    result = publish(config.blog_dir, job.get("text", ""), images, run=run)
    log_outcome(result)
    if result.ok:
        reply(mailer.receipt(result))
    else:
        reply(mailer.failure_notice(result.error or "unknown failure"))


def _fetch_stored_mime(config, message_id: str) -> bytes | None:
    return security.stored_message_mime(
        config, message_id,
        attempts=VERIFY_FETCH_ATTEMPTS, delay=VERIFY_FETCH_DELAY,
    )


def _job_images(job: dict) -> list:
    return [
        {
            "data": Path(image["path"]).read_bytes(),
            "mime": image["mime"],
            "alt": image.get("alt", ""),
            "filename": image.get("filename", ""),
        }
        for image in job.get("images", [])
    ]
