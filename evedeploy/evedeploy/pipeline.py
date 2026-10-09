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
import shlex
import shutil
import subprocess
from pathlib import Path

RSYNC_TARGET = "evegd@reclaim:/home/evegd/blog/_site/"
# The deploy server doubles as the canonical build cache: the PDFs it
# serves are byte-for-byte the .pdf_cache renders, the OG cards likewise,
# and the PDF content hashes (which decide whether a page re-renders) are
# kept beside them in a directory of their own. Any build machine pulls
# all three before building, so an unchanged page never re-renders or
# re-ships no matter which machine last built it.
CACHE_SERVER = "evegd@reclaim:/home/evegd/blog"
REMOTE_PDF_DIR = f"{CACHE_SERVER}/_site/PDF/"
REMOTE_OG_DIR = f"{CACHE_SERVER}/_site/images/og/"
REMOTE_HASH_DIR = f"{CACHE_SERVER}/.pdf_cache/"
PDF_CACHE = ".pdf_cache"
OG_CACHE = ".og_cache"
# Where a remote build host keeps its checkout (REMOTE_BUILD_DIR overrides).
DEFAULT_REMOTE_DIR = "~/build/martineve/blog"
# What the short-thought quick path commits before handing off remotely.
THOUGHT_PATHS = ("_data/thoughts.yml", "assets/thoughts")
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


def quick_deploy(root: Path, run=default_run, echo=print,
                 cache_sync: bool = True, commit_ledger: bool = False) -> bool:
    """Build the site, rsync it, and mention what the new thought links to.

    The fast path for short thoughts: no cover resize, no identifier
    sweeps or feed fetches, no ATProto publish, no git work, no
    repository deposits. The PDF and OG caches keep the build brisk and
    rsync ships only what changed. The one thing that follows the rsync
    is the thoughts-only webmention pass (receivers fetch the live
    source page, so it cannot come earlier); the ledger it writes is
    left for the caller to commit alongside the thought itself — unless
    ``commit_ledger`` asks for it to be committed and pushed here (the
    remote build host's case: its checkout is reset on every run, so
    anything left uncommitted there would be lost).
    """
    root = Path(root)
    if cache_sync:
        echo("==> Pulling the build cache from the server")
        pull_build_cache(root, run=run, echo=echo)
    echo("==> Building site")
    jekyll_build(root, run=run)
    echo("==> Deploying to server")
    ship_site(root, run=run, echo=echo, cache_sync=cache_sync)
    echo("==> Sending the thought's webmentions")
    if not send_webmentions(root, run=run, echo=echo, only_thoughts=True):
        echo("    (skipped or failed; continuing)")
    if commit_ledger and commit_sent_state(root, run=run):
        echo("    sent-webmentions ledger committed")
    echo("==> Done.")
    return True


def biron_deposit_new(root: Path, run=default_run, echo=print,
                      present=None) -> list:
    """Sync posts to BIROn; returns those newly stamped with a link.

    Runs ``./biron.sh backfill`` (deposits every post without a
    ``biron:`` key straight into the live archive and stamps the link
    into its front matter) then ``./biron.sh update`` (replaces the
    records of posts changed since their last shipment — EPrints has no
    versioning, so updates overwrite in place, same id and URL). Both
    attach the built PDF, so this must run after the jekyll build.
    Skipped until some BIRON_ setting appears in .env (BIRON_COOKIE=auto
    for browser-session auth, or BIRON_USERNAME/BIRON_PASSWORD);
    tolerant: a BIROn outage must never block a deploy.
    """
    root = Path(root)
    exists = present or (lambda relative: (root / relative).is_file())
    if not exists("biron.sh"):
        return []
    env_path = root / ".env"
    if not env_path.is_file() or "BIRON_" not in env_path.read_text():
        echo("    (skipped: no BIRON_ configuration in .env)")
        return []
    pending = posts_missing_marker(root, "biron:")
    try:
        run(["./biron.sh", "backfill"], cwd=root)
    except subprocess.CalledProcessError:
        echo("ERROR: BIROn deposit failed; the next deploy will retry.")
    try:
        run(["./biron.sh", "update"], cwd=root)
    except subprocess.CalledProcessError:
        echo("ERROR: BIROn update failed; the next deploy will retry.")
    still = set(posts_missing_marker(root, "biron:"))
    return [post for post in pending if post not in still]


def commit_biron_ledger(root: Path, run=default_run) -> bool:
    """Commit the BIROn ledgers if the sync pass changed them."""
    _step(run, ["git", "add", "_biron"], name="git add",
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
                     run=default_run, echo=print, present=None,
                     args=()) -> bool:
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
        run(cmd + [script, *args], cwd=root)
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


def send_webmentions(root: Path, run=default_run, echo=print, present=None,
                     only_thoughts: bool = False) -> bool:
    """Send outbound webmentions once the site is live; tolerant step.

    ``only_thoughts`` restricts the pass to short thoughts (the quick
    deploy's case: one new entry, no rescan of the post archive).
    """
    return _webmention_step(
        root, "_webmentions/send_webmentions.py",
        "WARNING: webmention send failed; unsent mentions retry next deploy.",
        run=run, echo=echo, present=present,
        args=("--only-thoughts",) if only_thoughts else ())


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
    """Push the built _site to the server.

    Every build rewrites every file, so rsync's default timestamp check
    would list and resend the whole site; comparing content (and ignoring
    directory times) keeps the log to the files that actually changed.
    """
    _step(
        run,
        [
            "rsync",
            "-avz",
            "--checksum",
            "--omit-dir-times",
            f"{root}/_site/",
            RSYNC_TARGET,
        ],
        name="rsync to server",
    )


def _cache_rsync(run, source, destination, extra=()) -> bool:
    """One tolerant cache transfer; False on failure, never fatal."""
    result = run(["rsync", "-az", "--update", *extra, source, destination],
                 check=False)
    return result.returncode == 0


def pull_build_cache(root: Path, run=default_run, echo=print) -> bool:
    """Converge the local PDF/OG caches on the server's copies.

    Three pulls, none deleting anything local and none overwriting a
    newer local file (a render from a local preview build survives):
    the served PDFs and their content hashes into .pdf_cache, the served
    OG cards into .og_cache. Returns False (after a warning) when any
    pull fails — the build then just renders what it cannot find.
    """
    root = Path(root)
    pdf_cache = root / PDF_CACHE
    og_cache = root / OG_CACHE
    pdf_cache.mkdir(exist_ok=True)
    og_cache.mkdir(exist_ok=True)
    ok = True
    for source, destination in ((REMOTE_PDF_DIR, pdf_cache),
                                (REMOTE_HASH_DIR, pdf_cache),
                                (REMOTE_OG_DIR, og_cache)):
        if not _cache_rsync(run, source, f"{destination}/"):
            echo(f"WARNING: build cache pull from {source} failed; "
                 "missing pages will render afresh.")
            ok = False
    return ok


def push_cache_hashes(root: Path, run=default_run, echo=print) -> bool:
    """Record this build's PDF content hashes on the server.

    Only the .hash files travel (the PDFs themselves are already there,
    shipped with the site). Tolerant: a failure just means the next
    machine to build re-renders the pages this one changed.
    """
    root = Path(root)
    pdf_cache = root / PDF_CACHE
    if not pdf_cache.is_dir():
        return False
    ok = _cache_rsync(run, f"{pdf_cache}/", REMOTE_HASH_DIR,
                      extra=("--include=*.hash", "--exclude=*"))
    if not ok:
        echo("WARNING: build cache hash push failed; the next build on "
             "another machine may re-render recently changed pages.")
    return ok


def ship_site(root: Path, run=default_run, echo=print,
              cache_sync: bool = True) -> None:
    """rsync the site, then record its PDF hashes on the server."""
    rsync_site(root, run=run)
    if cache_sync:
        push_cache_hashes(root, run=run, echo=echo)


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
    cache_sync: bool = True,
    cv: bool = True,
) -> bool:
    """Run the whole pipeline; returns True on deploy, False when aborted.

    ``confirm`` is called (no arguments) after the sequoia dry run; a falsy
    return aborts with nothing published. ``wait_roguescholar`` controls the
    tail: after the site is live, poll Rogue Scholar for the records of any
    posts deposited this run, and fold the stamp/rebuild/rsync that used to
    need a second deploy into this one. ``sequoia`` controls the ATProto
    publish: when False the dry run, confirmation gate and publish are all
    skipped (and the tool need not be installed) — nothing is gated, since
    the gate exists only to guard that irreversible publish. ``cache_sync``
    pulls the server's PDF/OG caches before the first build and records
    the new PDF hashes after each ship; ``cv`` controls the CV refresh
    (off on a remote build host, where the sibling checkout is absent
    and the CV files arrive committed from the local phase).
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

    if cv:
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

    if cache_sync:
        echo("==> Pulling the build cache from the server")
        if pull_build_cache(root, run=run, echo=echo):
            echo("    caches converged")

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
    ship_site(root, run=run, echo=echo, cache_sync=cache_sync)

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
                ship_site(root, run=run, echo=echo, cache_sync=cache_sync)

    # BIROn deposits go straight into the live archive with the final
    # built PDF from this run; new posts get their biron: link stamped
    # into the front matter, so the site reships to render it. Updates
    # replace changed posts' records in place (no site-visible change).
    echo("==> Syncing posts to BIROn")
    biron_stamped = biron_deposit_new(root, run=run, echo=echo)
    if biron_stamped:
        echo("==> Rebuilding with the new BIROn links")
        jekyll_build(root, run=run)
        git_commit_push(
            root, "chore(biron): stamp BIROn record links", run=run)
        ship_site(root, run=run, echo=echo, cache_sync=cache_sync)
    elif commit_biron_ledger(root, run=run):
        echo("    BIROn ledger committed")

    echo("==> Done.")
    return True



# --- remote build host -----------------------------------------------------

def _git_out(run, args, cwd) -> str:
    result = run(["git", *args], cwd=cwd, check=False, capture=True)
    return (getattr(result, "stdout", "") or "").strip()


def commit_thought(root: Path, run=default_run) -> bool:
    """Commit and push a freshly stored short thought (and its images)."""
    present = [p for p in THOUGHT_PATHS if (Path(root) / p).exists()]
    if not present:
        return False
    _step(run, ["git", "add", *present], name="git add", cwd=root)
    staged = run(["git", "diff", "--cached", "--quiet"], cwd=root, check=False)
    if staged.returncode == 0:
        return False
    _step(run, ["git", "commit", "-m", "fix(thought): add thought"],
          name="git commit", cwd=root)
    _step(run, ["git", "push"], name="git push", cwd=root)
    return True


def _remote_prepare_script(remote_dir: str, origin: str, branch: str) -> str:
    """Shell for the host: clone on first use, then track the pushed branch.

    The checkout is a build slave — every run resets it hard to what was
    just pushed, so nothing is ever edited there by hand. git's ssh is
    pinned to the forwarded agent: this runs without a TTY, and the
    host's own ssh config may steer such sessions to a desktop agent of
    its own that cannot sign (see remote_check).
    """
    return (
        'export GIT_SSH_COMMAND="ssh -o IdentityAgent=$SSH_AUTH_SOCK"; '
        f"set -e; mkdir -p $(dirname {remote_dir}); "
        f"if [ ! -d {remote_dir}/.git ]; then "
        f"git clone {shlex.quote(origin)} {remote_dir}; fi; "
        f"cd {remote_dir} && git fetch origin && "
        f"git checkout -q {shlex.quote(branch)} 2>/dev/null || "
        f"git checkout -q -b {shlex.quote(branch)} "
        f"origin/{shlex.quote(branch)}; "
        f"git reset --hard origin/{shlex.quote(branch)}"
    )


def _ssh(run, host, script, name, tty=False, agent=False, check=True):
    cmd = ["ssh"]
    if agent:
        cmd.append("-A")
    if tty:
        cmd.append("-t")
    cmd += [host, script]
    if not check:
        return run(cmd, check=False)
    return _step(run, cmd, name=name)


def _copy_to_host(run, host, source: Path, destination: str, name: str):
    _step(run, ["scp", "-q", str(source), f"{host}:{destination}"],
          name=name)


def remote_deploy(root: Path, host: str, remote_dir: str, message, args,
                  run=default_run, echo=print, resize: bool = True,
                  quick: bool = False, home=None) -> bool:
    """Prepare locally, push, then run the pipeline on the build host.

    For a low-bandwidth operator: everything that needs local resources or
    shrinks what has to travel happens here (cover resize, CV refresh, the
    commit and push — or, on the quick path, just committing the thought);
    everything heavy (Sequoia, feed fetches, the build, deposits, rsync,
    webmentions, the Rogue Scholar wait, BIROn) runs on ``host`` in its
    checkout at ``remote_dir``, via that checkout's own deploy.sh and so
    inside the same container image. Secrets that git does not carry
    (.env, the BIROn cookie) are copied across first; sequoia's
    credential store is seeded only when the host has none, so refreshed
    tokens there are never clobbered. The run streams to this terminal
    (a TTY, for the ATProto gate) with the local SSH agent forwarded, so
    the host signs commits and reaches the deploy server with this
    machine's keys. Afterwards a fast-forward pull collects whatever the
    host committed (deposit stamps, the webmention ledger).
    """
    root = Path(root)
    home = Path(home) if home else Path.home()

    if quick:
        echo("==> Committing the thought")
        if not commit_thought(root, run=run):
            echo("    (nothing new to commit)")
    else:
        echo("==> Checking cover image sizes")
        if not resize_covers(root, run=run, enabled=resize):
            echo("    (skipped)")
        echo("==> Refreshing CV")
        if not refresh_cv(root):
            echo(
                f"WARNING: {CV_SOURCE_DIR}/martin_paul_eve.{{pdf,html}} not "
                "found; keeping existing CV files."
            )
        echo("==> Committing and pushing")
        if not git_commit_push(root, message, run=run):
            echo("Nothing new to commit — working tree clean.")

    branch = _git_out(run, ["rev-parse", "--abbrev-ref", "HEAD"], root) or "main"
    origin = _git_out(run, ["remote", "get-url", "origin"], root)
    echo(f"==> Preparing {host}:{remote_dir} ({branch})")
    _ssh(run, host, _remote_prepare_script(remote_dir, origin, branch),
         name="remote checkout", agent=True)

    echo("==> Copying secrets to the build host")
    for name in (".env", ".biron_cookie"):
        if (root / name).is_file():
            _copy_to_host(run, host, root / name, f"{remote_dir}/{name}",
                          name=f"copy {name}")
    sequoia = home / ".config" / "sequoia" / "credentials.json"
    if sequoia.is_file():
        probe = _ssh(run, host, "test -f ~/.config/sequoia/credentials.json",
                     name="sequoia probe", check=False)
        if probe.returncode != 0:
            _ssh(run, host, "mkdir -p ~/.config/sequoia", name="sequoia dir")
            _copy_to_host(run, host, sequoia, "~/.config/sequoia/credentials.json",
                          name="copy sequoia credentials")

    remote_args = ["--local", "--no-resize", "--no-cv", *args]
    if message:
        remote_args.append(message)
    script = (f"cd {remote_dir} && ./deploy.sh "
              + " ".join(shlex.quote(a) for a in remote_args))
    echo(f"==> Running the pipeline on {host}")
    try:
        _ssh(run, host, script, name="remote build", tty=True, agent=True)
    except DeployError as exc:
        raise DeployError(f"remote build on {host} failed: {exc}") from exc

    echo("==> Pulling what the build host committed")
    _step(run, ["git", "pull", "--ff-only"], name="git pull", cwd=root)
    echo("==> Done.")
    return True


def remote_check(root: Path, host: str, remote_dir: str, run=default_run,
                 echo=print) -> bool:
    """Try every hop a remote build needs and report each; True if all pass.

    Nothing is changed anywhere. The GitHub check is ssh's `-T` handshake,
    which exits 1 on success (GitHub offers no shell), so that one passes
    on exit 0 or 1. The two onward hops pin the forwarded agent
    explicitly: the host's own ssh config may steer sessions without a
    TTY (which these are) to a desktop agent of its own, which cannot
    sign. The real run is unaffected — inside the container the forwarded
    agent answers at the desktop agents' paths too — but the check must
    exercise the agent the run will actually use.
    """
    hop = "ssh -o BatchMode=yes -o IdentityAgent=$SSH_AUTH_SOCK"
    checks = [
        ("ssh to the build host", "true", {0}),
        ("docker on the build host", "command -v docker >/dev/null", {0}),
        ("build host -> deploy server (reclaim) via forwarded agent",
         f"{hop} evegd@reclaim true", {0}),
        ("build host -> github.com via forwarded agent",
         f"{hop} -T git@github.com", {0, 1}),
    ]
    all_ok = True
    for label, script, good in checks:
        result = run(["ssh", "-A", host, script], check=False)
        ok = result.returncode in good
        all_ok = all_ok and ok
        echo(f"{'OK  ' if ok else 'FAIL'} {label}")
    # Informational: the first real run clones the checkout itself.
    present = run(["ssh", "-A", host, f"test -d {remote_dir}/.git"],
                  check=False).returncode == 0
    echo(f"{'OK  ' if present else 'note'} checkout {remote_dir} "
         f"{'present' if present else 'not yet cloned (the first run clones it)'}")
    echo("All checks passed." if all_ok else
         "Some checks failed; fix those before a remote deploy.")
    return all_ok
