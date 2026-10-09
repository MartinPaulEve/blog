"""Command-line entry point for the eve.gd deployment pipeline."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import click

from evedeploy.banner import print_banner
from evedeploy.pipeline import (
    DEFAULT_REMOTE_DIR,
    PREVIEW_PORT,
    DeployError,
    build_site,
    deploy,
    quick_deploy,
    remote_check,
    remote_deploy,
    serve_site,
)


def find_root(start: Path) -> Path:
    """The blog root: the nearest ancestor (or start) with a _config.yml."""
    start = Path(start).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "_config.yml").is_file():
            return candidate
    raise FileNotFoundError(f"No _config.yml found at or above {start}")


@click.command()
@click.argument("message", required=False)
@click.option(
    "--no-resize", is_flag=True, help="Skip the cover-image resize step."
)
@click.option(
    "--yes",
    is_flag=True,
    help="Publish without the interactive confirmation gate.",
)
@click.option(
    "--root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Blog root (default: found from the working directory).",
)
@click.option(
    "--build-only",
    is_flag=True,
    help="Just build the site (PDFs included) to _site for local preview; "
    "no publish, commit or deploy.",
)
@click.option(
    "--no-server",
    is_flag=True,
    help="With --build-only: skip the preview server after the build.",
)
@click.option(
    "--no-rs-wait",
    is_flag=True,
    help="Skip waiting for Rogue Scholar to harvest new posts after the "
    "rsync (the next deploy stamps their links instead).",
)
@click.option(
    "--no-sequoia",
    is_flag=True,
    help="Skip the Sequoia/ATProto publish step (dry run, confirmation "
    "gate and publish); everything else still builds and deploys.",
)
@click.option(
    "--quick",
    is_flag=True,
    help="Fast path: jekyll build + rsync only — no resize, sequoia, "
    "git, deposits or feed fetches (used after posting a short thought).",
)
@click.option(
    "--local",
    is_flag=True,
    help="Run the pipeline here even when REMOTE_BUILD_HOST is set "
    "(what the remote build host itself runs).",
)
@click.option(
    "--remote-check",
    "check_remote",
    is_flag=True,
    help="Verify every hop a remote build needs (ssh, docker, checkout, "
    "the host's reach to the deploy server and GitHub) and exit.",
)
@click.option(
    "--no-cache-sync",
    is_flag=True,
    help="Do not pull the server's PDF/OG caches before building or push "
    "the PDF hashes after shipping.",
)
@click.option(
    "--no-cv",
    is_flag=True,
    help="Skip the CV refresh from ../eprintsToCV.",
)
def main(message, no_resize, yes, root, build_only, no_server, no_rs_wait,
         no_sequoia, quick, local, check_remote, no_cache_sync, no_cv):
    """Build, publish and deploy the eve.gd blog.

    With REMOTE_BUILD_HOST set (in .env), everything but the local
    preparation runs on that host over SSH — see remote_deploy — unless
    --local or --build-only is given. REMOTE_BUILD_DIR names the host's
    checkout (default: ~/build/martineve/blog).
    """
    print_banner()

    if root is None:
        try:
            root = find_root(Path.cwd())
        except FileNotFoundError as exc:
            raise click.ClickException(str(exc)) from exc

    host = os.environ.get("REMOTE_BUILD_HOST") or None
    remote_dir = os.environ.get("REMOTE_BUILD_DIR") or DEFAULT_REMOTE_DIR

    if check_remote:
        if not host:
            raise click.ClickException(
                "REMOTE_BUILD_HOST is not set (put it in .env).")
        if not remote_check(root, host=host, remote_dir=remote_dir,
                            echo=click.echo):
            raise click.ClickException("remote build checks failed")
        return

    if host and not local and not build_only:
        forwarded = []
        if quick:
            forwarded.append("--quick")
        if yes:
            forwarded.append("--yes")
        if no_rs_wait:
            forwarded.append("--no-rs-wait")
        if no_sequoia:
            forwarded.append("--no-sequoia")
        if no_cache_sync:
            forwarded.append("--no-cache-sync")
        if message is None and not quick:
            message = datetime.now().astimezone().strftime(
                "Publish %Y-%m-%d %H:%M"
            )
        try:
            remote_deploy(
                root, host=host, remote_dir=remote_dir, message=message,
                args=forwarded, echo=click.echo, resize=not no_resize,
                quick=quick,
            )
        except DeployError as exc:
            raise click.ClickException(str(exc)) from exc
        return

    if quick:
        try:
            quick_deploy(root=root, echo=click.echo,
                         cache_sync=not no_cache_sync, commit_ledger=local)
        except DeployError as exc:
            raise click.ClickException(str(exc)) from exc
        return

    if build_only:
        try:
            build_site(root=root, resize=not no_resize, echo=click.echo)
        except DeployError as exc:
            raise click.ClickException(str(exc)) from exc
        if no_server:
            click.echo(
                "    Preview with: python3 -m http.server -d "
                f"{root}/_site {PREVIEW_PORT}"
            )
        else:
            serve_site(root=root, echo=click.echo)
        return

    if message is None:
        message = datetime.now().astimezone().strftime(
            "Publish %Y-%m-%d %H:%M"
        )

    if yes:
        confirm = lambda: True
    else:
        confirm = lambda: click.confirm(
            "Publish these to ATProto for real?", default=False
        )

    try:
        deploy(
            root=root,
            message=message,
            resize=not no_resize,
            confirm=confirm,
            echo=click.echo,
            wait_roguescholar=not no_rs_wait,
            sequoia=not no_sequoia,
            cache_sync=not no_cache_sync,
            cv=not no_cv,
        )
    except DeployError as exc:
        raise click.ClickException(str(exc)) from exc
