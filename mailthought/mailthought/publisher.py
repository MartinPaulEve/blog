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

import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from . import drafts, mailer

COMMIT_MESSAGE = "chore(thoughts): add {thought_id} via mail gateway"

THOUGHT_BASE = [
    "uv", "run", "--env-file", ".env",
    "--project", "thought_composer", "thought",
]

STORED_RE = re.compile(r"^Stored thought (\d+) \((\d+) post\(s\)\)\.")
POST_MARKER_RE = re.compile(r"^--- post \d+ ---$")

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
    """The status line and per-post segments from `thought --dry-run`."""
    lines = (stdout or "").splitlines()
    status = lines[0].strip() if lines else ""
    posts = []
    current = None
    for line in lines[1:]:
        if POST_MARKER_RE.match(line.strip()):
            if current is not None:
                posts.append("\n".join(current).strip("\n"))
            current = []
        elif current is not None:
            current.append(line)
    if current is not None:
        posts.append("\n".join(current).strip("\n"))
    return DryRunResult(status=status, posts=posts)


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


def process_job(job: dict, config, run=default_run, send=None) -> None:
    """Execute one persisted inbox job and mail the outcome back.

    ``job`` is the dict app.py persisted before returning 200:
    {"kind", "sender", "message_id", "subject", "text", "draft_id",
    "images": [{"path", "mime", "alt", "filename"}]}. ``send`` is
    mailer.send_email-shaped, injectable for tests.
    """
    send = send or mailer.send_email
    to = job["sender"]
    in_reply_to = job.get("message_id") or None

    def reply(pair):
        subject, body = pair
        send(config, to, subject, body, in_reply_to=in_reply_to)

    kind = job.get("kind")

    if kind == "bad_reply":
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
        reply(mailer.dry_run_report(draft_id, result, image_count=len(images)))
        return

    if kind == "post_draft":
        draft_id = job.get("draft_id") or ""
        draft = drafts.load_draft(config.drafts_dir, draft_id)
        if draft is None:
            reply(mailer.missing_draft_notice(draft_id))
            return
        result = publish(config.blog_dir, draft["text"], draft["images"], run=run)
        if result.ok:
            drafts.delete_draft(config.drafts_dir, draft_id)
            reply(mailer.receipt(result))
        else:
            reply(mailer.failure_notice(result.error or "unknown failure"))
        return

    images = _job_images(job)
    result = publish(config.blog_dir, job.get("text", ""), images, run=run)
    if result.ok:
        reply(mailer.receipt(result))
    else:
        reply(mailer.failure_notice(result.error or "unknown failure"))


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
