"""Command-line entry point for the eve.gd deployment pipeline."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import click

from evedeploy.banner import print_banner
from evedeploy.pipeline import (
    PREVIEW_PORT,
    DeployError,
    build_site,
    deploy,
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
def main(message, no_resize, yes, root, build_only, no_server):
    """Build, publish and deploy the eve.gd blog."""
    print_banner()

    if root is None:
        try:
            root = find_root(Path.cwd())
        except FileNotFoundError as exc:
            raise click.ClickException(str(exc)) from exc

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
        )
    except DeployError as exc:
        raise click.ClickException(str(exc)) from exc
