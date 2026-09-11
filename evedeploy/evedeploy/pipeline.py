"""The deployment pipeline: everything newdeploy.sh did, step by step.

Order of operations (faithful to the shell script):
resize covers → sequoia dry-run → confirmation gate (skipped when the dry
run reports nothing new to publish) → sequoia publish →
refresh CV from ../eprintsToCV → fetch webmentions (so the build renders
fresh mentions) → fetch Last.fm stats (so the sidebar widget renders fresh
listening data) → stamp pending Rogue Scholar links from earlier deploys →
jekyll build → deposit new posts to KC Works and rebuild so their record
links render → git commit + push → rsync the built _site to the server →
send outbound webmentions (receivers verify the live source page, so this
must follow the rsync) → commit the sent-webmentions ledger → wait for
Rogue Scholar to harvest the new posts, then stamp, rebuild, commit and
rsync once more (folding the old "second deploy" into this run).

Every step takes an injectable ``run`` callable (subprocess.run-shaped) so
the pipeline is unit-testable without touching the real system.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

RSYNC_TARGET = "evegd@reclaim:/home/evegd/blog/_site/"
CV_SOURCE_DIR = Path("../eprintsToCV/output")
MIN_NODE_MAJOR = 19
PREVIEW_PORT = 8000
RS_FETCHER = "_identifiers/fetch_roguescholar.py"
# Post-rsync harvest wait: 6 attempts, 5 sleeps of 120s = a 10-minute budget.
RS_WAIT_ATTEMPTS = 6
RS_WAIT_INTERVAL = 120.0


class DeployError(RuntimeError):
    """A pipeline step that failed and should stop the deployment."""


def default_run(cmd, cwd=None, check=True, capture=False):
    """Run a command; the pipeline's only touchpoint with the real system."""
    return subprocess.run(
        cmd, cwd=cwd, check=check, capture_output=capture, text=True
    )


def _step(run, cmd, name, cwd=None):
    try:
        return run(cmd, cwd=cwd)
    except subprocess.CalledProcessError as exc:
        raise DeployError(f"{name} failed (exit {exc.returncode})") from exc


def check_preflight(run=default_run, which=shutil.which) -> None:
    """Sequoia must be on PATH; node, if present at all, must be >= 19.

    The Nix-packaged sequoia wraps its own Node, so a PATH node is
    optional; only the minimum version is enforced when one exists.
    """
    if not which("sequoia"):
        raise DeployError("sequoia not found on PATH")
    if which("node"):
        result = run(
            ["node", "-p", 'process.versions.node.split(".")[0]'],
            check=False,
            capture=True,
        )
        try:
            major = int((result.stdout or "0").strip() or 0)
        except ValueError:
            major = 0
        if major < MIN_NODE_MAJOR:
            raise DeployError(
                f"Node {major} detected; sequoia needs Node >= "
                f"{MIN_NODE_MAJOR}. Switch to a newer Node first."
            )


def resize_covers(root: Path, run=default_run, enabled: bool = True) -> bool:
    """Shrink oversized cover images; returns True when the step ran."""
    if not enabled or not (root / "resize_covers.py").is_file():
        return False
    _step(
        run,
        [
            "uv",
            "run",
            "--with",
            "pillow",
            "--with",
            "python-frontmatter",
            "./resize_covers.py",
        ],
        name="cover resize",
        cwd=root,
    )
    return True


NOTHING_TO_PUBLISH = re.compile(r"nothing to publish", re.IGNORECASE)


def sequoia_dry_run(run=default_run, echo=print) -> bool:
    """Preview the ATProto publish without writing anything.

    Returns True when the preview has something to publish, False when it
    reports the repo is up to date. The captured preview is echoed so the
    operator still sees exactly what would go out before deciding.
    """
    try:
        result = run(["sequoia", "publish", "--dry-run"], capture=True)
    except subprocess.CalledProcessError as exc:
        raise DeployError(
            f"sequoia dry run failed (exit {exc.returncode})") from exc
    output = ((getattr(result, "stdout", "") or "")
              + (getattr(result, "stderr", "") or ""))
    if output.strip():
        echo(output.rstrip("\n"))
    return not NOTHING_TO_PUBLISH.search(output)


def sequoia_publish(run=default_run) -> None:
    """Publish new posts to ATProto for real."""
    _step(run, ["sequoia", "publish"], name="sequoia publish")


def refresh_cv(root: Path) -> bool:
    """Copy the CV PDF/HTML from the sibling eprintsToCV checkout.

    Returns True when both files were found and copied; False (leaving the
    existing files alone) when the source is missing.
    """
    source = (root / CV_SOURCE_DIR).resolve()
    pdf = source / "martin_paul_eve.pdf"
    html = source / "martin_paul_eve.html"
    if not (pdf.is_file() and html.is_file()):
        return False
    shutil.copy(pdf, root / "c-v" / "Eve-CV.pdf")
    shutil.copy(html, root / "_includes" / "publications.html")
    return True


def jekyll_build(root: Path, run=default_run) -> None:
    """Build the site with plain jekyll.

    Plain jekyll, not `bundle exec`: the Nix jekyll (full variant) carries
    its own bundle incl. jekyll-feed; bundler would demand a local gem
    install. No --incremental: it skips pages that iterate site.posts
    (feed.xml, feed_all.xml), leaving them stale when a post is added.

    That Nix jekyll runs its own Bundler.setup against a read-only nix-store
    Gemfile which still declares the legacy :mingw/:mswin/:x64_mingw platform
    symbols, so every build prints a Bundler deprecation we cannot fix at the
    source. Silence it here (respecting an explicit override).
    """
    os.environ.setdefault("BUNDLE_SILENCE_DEPRECATIONS", "true")
    _step(run, ["jekyll", "build"], name="jekyll build", cwd=root)


def posts_missing_marker(root: Path, marker: str) -> list:
    """Relative paths of _posts entries whose front matter lacks ``marker``."""
    posts_dir = Path(root) / "_posts"
    if not posts_dir.is_dir():
        return []
    missing = []
    for path in sorted(posts_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
        front = match.group(1) if match else ""
        if not any(line.startswith(marker) for line in front.splitlines()):
            missing.append(f"_posts/{path.name}")
    return missing


def stamp_roguescholar_ids(root: Path, pending, run=default_run, echo=print,
                           attempts: int = 1,
                           interval: float = RS_WAIT_INTERVAL,
                           present=None) -> list:
    """Stamp Rogue Scholar links into pending posts; returns those stamped.

    Runs the _identifiers fetcher, which matches the posts against the
    Rogue Scholar community records and writes ``roguescholar:`` front
    matter for any that have been harvested. A non-zero exit just means
    some posts have no record yet (Rogue Scholar pulls the feed on its own
    cycle), so the call is never allowed to fail the deploy.
    """
    root = Path(root)
    exists = present or (lambda relative: (root / relative).is_file())
    if not pending or not exists(RS_FETCHER):
        return []
    cmd = ["uv", "run", "--with", "pyyaml", "--with", "certifi", RS_FETCHER]
    if attempts > 1:
        cmd += ["--attempts", str(attempts), "--interval", str(int(interval))]
    run(cmd + list(pending), cwd=root, check=False)
    still = set(posts_missing_marker(root, "roguescholar:"))
    return [post for post in pending if post not in still]


def kcworks_deposit_new(root: Path, run=default_run, echo=print,
                        present=None) -> list:
    """Deposit posts new to KC Works; returns those stamped with a record.

    Wraps ``./kcworks.sh backfill``, which deposits and publishes every
    post without a ``kcworks:`` front-matter record (attaching the built
    PDF, so this must run after the jekyll build) and stamps the record
    URL back into the post. Tolerant: a KC Works outage must never block
    a deploy — undeposited posts are picked up by the next run.
    """
    root = Path(root)
    exists = present or (lambda relative: (root / relative).is_file())
    pending = posts_missing_marker(root, "kcworks:")
    if not pending or not exists("kcworks.sh"):
        return []
    try:
        run(["./kcworks.sh", "backfill"], cwd=root)
    except subprocess.CalledProcessError:
        echo("ERROR: KC Works deposit failed; the next deploy will retry.")
    still = set(posts_missing_marker(root, "kcworks:"))
    return [post for post in pending if post not in still]


def quick_deploy(root: Path, run=default_run, echo=print) -> bool:
    """Build the site and rsync it — nothing else.

    The fast path for short thoughts: no cover resize, no identifier
    sweeps or feed fetches, no ATProto publish, no git work, no
    repository deposits. The PDF and OG caches keep the build brisk and
    rsync ships only what changed.
    """
    root = Path(root)
    echo("==> Building site")
    jekyll_build(root, run=run)
    echo("==> Deploying to server")
    rsync_site(root, run=run)
    echo("==> Done.")
    return True


def biron_deposit_new(root: Path, run=default_run, echo=print,
                      present=None) -> bool:
    """Deposit posts new to BIROn; returns True when the backfill ran.

    Wraps ``./biron.sh backfill``, which SWORD-deposits every post
    without a ``biron:`` front-matter key that is neither pending in
    the _biron/deposited.yml ledger nor listed in _biron/skip.yml
    (attaching the built PDF, so this must run after the jekyll build).
    Deposits land in the repository's review queue, so nothing is
    stamped back here — the _biron fetch sweep adds the biron: key once
    the record goes live. Skipped until some BIRON_ setting appears in
    .env (BIRON_COOKIE=auto for browser-session auth, or
    BIRON_USERNAME/BIRON_PASSWORD); tolerant: a BIROn outage must never
    block a deploy.
    """
    root = Path(root)
    exists = present or (lambda relative: (root / relative).is_file())
    if not exists("biron.sh"):
        return False
    env_path = root / ".env"
    if not env_path.is_file() or "BIRON_" not in env_path.read_text():
        echo("    (skipped: no BIRON_ configuration in .env)")
        return False
    try:
        run(["./biron.sh", "backfill"], cwd=root)
    except subprocess.CalledProcessError:
        echo("ERROR: BIROn deposit failed; the next deploy will retry.")
        return False
    return True


def commit_biron_ledger(root: Path, run=default_run) -> bool:
    """Commit the pending-deposit ledger if the backfill changed it."""
    _step(run, ["git", "add", "_biron/deposited.yml"], name="git add",
          cwd=root)
    staged = run(["git", "diff", "--cached", "--quiet"], cwd=root, check=False)
    if staged.returncode == 0:
        return False
    _step(run, ["git", "commit", "-m",
                "chore(biron): record pending BIROn deposits"],
          name="git commit", cwd=root)
    _step(run, ["git", "push"], name="git push", cwd=root)
    return True


def git_commit_push(root: Path, message: str, run=default_run) -> bool:
    """Stage everything; commit and push if there is anything to commit.

    Returns True when a commit was made, False when the tree was clean.
    """
    _step(run, ["git", "add", "-A"], name="git add", cwd=root)
    staged = run(["git", "diff", "--cached", "--quiet"], cwd=root, check=False)
    if staged.returncode == 0:
        return False
    _step(run, ["git", "commit", "-m", message], name="git commit", cwd=root)
    _step(run, ["git", "push"], name="git push", cwd=root)
    return True


def _webmention_step(root: Path, script: str, warning: str,
                     run=default_run, echo=print, present=None) -> bool:
    """Run a data-fetch script as a tolerant pipeline step.

    Returns True when the script ran cleanly, False when it was skipped (no
    script in this checkout) or failed — an API outage (webmention.io, the
    Last.fm API) or a flaky receiver must never block a deploy.
    """
    root = Path(root)
    exists = present or (lambda relative: (root / relative).is_file())
    if not exists(script):
        return False
    cmd = ["uv", "run"]
    if (root / ".env").is_file():
        cmd += ["--env-file", ".env"]  # carries the API tokens
    try:
        run(cmd + [script], cwd=root)
    except subprocess.CalledProcessError:
        echo(warning)
        return False
    return True


def fetch_webmentions(root: Path, run=default_run, echo=print, present=None) -> bool:
    """Pull received webmentions into _data before the build; tolerant step."""
    return _webmention_step(
        root, "_webmentions/fetch_webmentions.py",
        "WARNING: webmention fetch failed; building with existing data.",
        run=run, echo=echo, present=present)


def fetch_lastfm(root: Path, run=default_run, echo=print, present=None) -> bool:
    """Pull Last.fm listening stats into _data before the build; tolerant step."""
    return _webmention_step(
        root, "_lastfm/fetch_lastfm.py",
        "ERROR: Last.fm fetch failed; building with existing data.",
        run=run, echo=echo, present=present)


def send_webmentions(root: Path, run=default_run, echo=print, present=None) -> bool:
    """Send outbound webmentions once the site is live; tolerant step."""
    return _webmention_step(
        root, "_webmentions/send_webmentions.py",
        "WARNING: webmention send failed; unsent mentions retry next deploy.",
        run=run, echo=echo, present=present)


def commit_sent_state(root: Path, run=default_run) -> bool:
    """Commit the sent-webmentions ledger if the send pass changed it."""
    _step(run, ["git", "add", "_webmentions/sent.json"], name="git add", cwd=root)
    staged = run(["git", "diff", "--cached", "--quiet"], cwd=root, check=False)
    if staged.returncode == 0:
        return False
    _step(run, ["git", "commit", "-m",
                "chore(webmentions): record sent webmentions"],
          name="git commit", cwd=root)
    _step(run, ["git", "push"], name="git push", cwd=root)
    return True


def rsync_site(root: Path, run=default_run) -> None:
    """Push the built _site to the server."""
    _step(
        run,
        ["rsync", "-avz", f"{root}/_site/", RSYNC_TARGET],
        name="rsync to server",
    )


def build_site(
    root: Path,
    resize: bool = True,
    run=default_run,
    echo=print,
) -> None:
    """Build the site locally to _site (PDF editions included); no publish.

    The local-preview path: cover resize plus jekyll build, nothing else.
    No sequoia preflight (the publish toolchain is not needed to build),
    no CV refresh, no git, no rsync. The PDF editions are generated inside
    `jekyll build` itself by the _plugins/pdf_pages.rb post_write hook.
    """
    root = Path(root)
    echo("==> Checking cover image sizes")
    if not resize_covers(root, run=run, enabled=resize):
        echo("    (skipped)")
    echo("==> Building site (PDF editions included)")
    jekyll_build(root, run=run)
    echo(f"==> Done. Site written to {root / '_site'}")


def port_is_free(port: int) -> bool:
    """True when nothing is listening on the port on localhost."""
    import socket

    with socket.socket() as sock:
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def serve_site(root: Path, run=default_run, echo=print, port_free=None) -> None:
    """Serve the built _site on localhost for preview; blocks until Ctrl+C.

    A busy PREVIEW_PORT (a preview already running, say) falls over to the
    next free port rather than crashing into Address-already-in-use.
    check=False because stopping the server with Ctrl+C makes it exit
    non-zero; that is the normal way out, not a failure.
    """
    root = Path(root)
    free = port_free or port_is_free
    candidates = range(PREVIEW_PORT, PREVIEW_PORT + 10)
    port = next((p for p in candidates if free(p)), None)
    if port is None:
        raise DeployError(
            f"no free preview port between {candidates[0]} and {candidates[-1]}"
        )
    echo(f"==> Serving preview at http://127.0.0.1:{port}/ (Ctrl+C to stop)")
    try:
        run(
            [
                "python3",
                "-m",
                "http.server",
                "--bind",
                "127.0.0.1",
                "-d",
                f"{root}/_site",
                str(port),
            ],
            check=False,
        )
    except KeyboardInterrupt:
        pass
    echo("==> Preview server stopped.")


def deploy(
    root: Path,
    message: str,
    resize: bool = True,
    confirm=None,
    run=default_run,
    echo=print,
    which=shutil.which,
    wait_roguescholar: bool = True,
    sequoia: bool = True,
) -> bool:
    """Run the whole pipeline; returns True on deploy, False when aborted.

    ``confirm`` is called (no arguments) after the sequoia dry run; a falsy
    return aborts with nothing published. ``wait_roguescholar`` controls the
    tail: after the site is live, poll Rogue Scholar for the records of any
    posts deposited this run, and fold the stamp/rebuild/rsync that used to
    need a second deploy into this one. ``sequoia`` controls the ATProto
    publish: when False the dry run, confirmation gate and publish are all
    skipped (and the tool need not be installed) — nothing is gated, since
    the gate exists only to guard that irreversible publish.
    """
    root = Path(root)
    if sequoia:
        check_preflight(run=run, which=which)

    echo("==> Checking cover image sizes")
    if not resize_covers(root, run=run, enabled=resize):
        echo("    (skipped)")

    if sequoia:
        echo("==> Sequoia dry run — nothing is published yet")
        pending = sequoia_dry_run(run=run, echo=echo)

        # Only gate on the irreversible ATProto publish. When the dry run
        # shows nothing new to publish there is nothing to guard, so proceed
        # without prompting (edits still build and ship); otherwise honour
        # the gate.
        if pending:
            if confirm is None or not confirm():
                echo(
                    "Aborted — nothing published. Local build/resize changes "
                    "are left uncommitted."
                )
                return False
        else:
            echo(
                "    Nothing new to publish to ATProto — no confirmation "
                "needed."
            )

        echo("==> Publishing to ATProto")
        sequoia_publish(run=run)
    else:
        echo("==> Skipping Sequoia/ATProto publish (--no-sequoia)")

    echo("==> Refreshing CV")
    if not refresh_cv(root):
        echo(
            f"WARNING: {CV_SOURCE_DIR}/martin_paul_eve.{{pdf,html}} not "
            "found; keeping existing CV files."
        )

    echo("==> Fetching webmentions")
    if not fetch_webmentions(root, run=run, echo=echo):
        echo("    (skipped or failed; continuing)")

    echo("==> Fetching Last.fm stats")
    if not fetch_lastfm(root, run=run, echo=echo):
        echo("    (skipped or failed; continuing)")

    # Posts from earlier deploys whose Rogue Scholar record has appeared
    # since get their link now, so this build renders it — the self-healing
    # half of avoiding a second deploy run.
    echo("==> Stamping pending Rogue Scholar links")
    swept = stamp_roguescholar_ids(
        root, posts_missing_marker(root, "roguescholar:"), run=run, echo=echo)
    if swept:
        echo(f"    stamped {len(swept)} post(s)")
    else:
        echo("    (none pending or not yet harvested)")

    echo("==> Building site")
    jekyll_build(root, run=run)

    # The deposit attaches the PDF from the build above; the stamp it
    # writes back then needs one more (cache-warm) build so the KC Works
    # link is in the HTML before the rsync.
    echo("==> Depositing new posts to KC Works")
    deposited = kcworks_deposit_new(root, run=run, echo=echo)
    if deposited:
        echo("==> Rebuilding with the new KC Works links")
        jekyll_build(root, run=run)
    else:
        echo("    (no new posts)")

    echo("==> Committing and pushing")
    if not git_commit_push(root, message, run=run):
        echo("Nothing new to commit — working tree clean.")

    echo("==> Deploying to server")
    rsync_site(root, run=run)

    # Only now can mentions go out: receivers verify the live source page.
    echo("==> Sending outbound webmentions")
    if not send_webmentions(root, run=run, echo=echo):
        echo("    (skipped or failed; continuing)")
    if commit_sent_state(root, run=run):
        echo("    sent-webmentions ledger committed")

    # The other half: Rogue Scholar can only harvest the post once it is
    # live, so poll for the record now and ship the stamped link in the
    # same run. Bounded; giving up is fine — the pre-build sweep above
    # picks the link up on the next deploy.
    if wait_roguescholar:
        fresh = set(posts_missing_marker(root, "roguescholar:"))
        fresh = [post for post in deposited if post in fresh]
        if fresh:
            echo("==> Waiting for Rogue Scholar to harvest the new post(s) "
                 "— up to 10 minutes; Ctrl+C stops the wait (the site is "
                 "already live)")
            try:
                stamped = stamp_roguescholar_ids(
                    root, fresh, run=run, echo=echo,
                    attempts=RS_WAIT_ATTEMPTS, interval=RS_WAIT_INTERVAL)
                if not stamped:
                    echo("    not harvested in time; the next deploy picks "
                         "the links up automatically")
            except KeyboardInterrupt:
                stamped = []
                echo("    wait interrupted; the next deploy picks the links "
                     "up automatically")
            if stamped:
                echo("==> Redeploying with the Rogue Scholar links")
                jekyll_build(root, run=run)
                git_commit_push(
                    root,
                    "chore(identifiers): stamp Rogue Scholar record links",
                    run=run)
                rsync_site(root, run=run)

    # BIROn deposits ride SWORD into the repository's review queue; the
    # attached PDF is the final built edition from this run, and the
    # biron: key arrives later via the _biron sweep once records go live.
    echo("==> Depositing new posts to BIROn")
    if biron_deposit_new(root, run=run, echo=echo):
        if commit_biron_ledger(root, run=run):
            echo("    deposit ledger committed")
    else:
        echo("    (skipped or failed; continuing)")

    echo("==> Done.")
    return True
