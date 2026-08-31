"""The deployment pipeline: everything newdeploy.sh did, step by step.

Order of operations (faithful to the shell script):
resize covers → sequoia dry-run → confirmation gate → sequoia publish →
refresh CV from ../eprintsToCV → jekyll build → git commit + push → rsync
the built _site to the server.

Every step takes an injectable ``run`` callable (subprocess.run-shaped) so
the pipeline is unit-testable without touching the real system.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

RSYNC_TARGET = "evegd@reclaim:/home/evegd/blog/_site/"
CV_SOURCE_DIR = Path("../eprintsToCV/output")
MIN_NODE_MAJOR = 19


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


def sequoia_dry_run(run=default_run) -> None:
    """Preview the ATProto publish without writing anything."""
    _step(run, ["sequoia", "publish", "--dry-run"], name="sequoia dry run")


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
    """
    _step(run, ["jekyll", "build"], name="jekyll build", cwd=root)


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
    echo("    Preview with: python3 -m http.server -d _site 8000")


def deploy(
    root: Path,
    message: str,
    resize: bool = True,
    confirm=None,
    run=default_run,
    echo=print,
    which=shutil.which,
) -> bool:
    """Run the whole pipeline; returns True on deploy, False when aborted.

    ``confirm`` is called (no arguments) after the sequoia dry run; a falsy
    return aborts with nothing published.
    """
    root = Path(root)
    check_preflight(run=run, which=which)

    echo("==> Checking cover image sizes")
    if not resize_covers(root, run=run, enabled=resize):
        echo("    (skipped)")

    echo("==> Sequoia dry run — nothing is published yet")
    sequoia_dry_run(run=run)

    if confirm is None or not confirm():
        echo(
            "Aborted — nothing published. Local build/resize changes are "
            "left uncommitted."
        )
        return False

    echo("==> Publishing to ATProto")
    sequoia_publish(run=run)

    echo("==> Refreshing CV")
    if not refresh_cv(root):
        echo(
            f"WARNING: {CV_SOURCE_DIR}/martin_paul_eve.{{pdf,html}} not "
            "found; keeping existing CV files."
        )

    echo("==> Building site")
    jekyll_build(root, run=run)

    echo("==> Committing and pushing")
    if not git_commit_push(root, message, run=run):
        echo("Nothing new to commit — working tree clean.")

    echo("==> Deploying to server")
    rsync_site(root, run=run)

    echo("==> Done.")
    return True
