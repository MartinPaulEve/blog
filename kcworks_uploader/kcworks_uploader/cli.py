"""Command-line entry point: upload one blog post to KC Works as a draft."""

import argparse
import json
import os
import sys
from pathlib import Path

from .client import KCWorksClient, KCWorksError
from .metadata import build_metadata
from .posts import canonical_url, find_pdf, parse_post, post_slug

DEFAULT_BASE_URL = "https://works.hcommons.org/api"
TOKEN_ENV_VAR = "KCWORKS_API_TOKEN"


def deposit_url(base_url: str, draft_id: str) -> str:
    """The browser URL where a draft can be reviewed and edited."""
    root = base_url.rstrip("/")
    root = root.removesuffix("/api")
    return f"{root}/uploads/{draft_id}"


def upload_post(
    post_path: Path,
    client,
    include_doi: bool = True,
    pdf_path: Path | None = None,
) -> dict:
    """Create a KC Works draft for a post and attach its markdown and PDF.

    Returns {"id", "edit_url", "files", "record"} for the created draft.
    """
    post_path = Path(post_path)
    post = parse_post(post_path)
    slug = post_slug(post_path)
    record = build_metadata(post, canonical_url(slug), include_doi=include_doi)
    if pdf_path is not None:
        pdf = Path(pdf_path)
    else:
        pdf = find_pdf(post_path.parent.parent, slug)

    draft = client.create_draft(record)
    files = client.upload_files(draft["id"], [post_path, pdf])
    return {
        "id": draft["id"],
        "edit_url": deposit_url(client.base_url, draft["id"]),
        "files": files,
        "record": draft,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="kcworks-upload",
        description=(
            "Upload a blog post to KC Works as a draft record, attaching "
            "the markdown source and the built PDF edition."
        ),
    )
    parser.add_argument("post", type=Path, help="path to the _posts/*.md file")
    parser.add_argument(
        "--token",
        default=os.environ.get(TOKEN_ENV_VAR),
        help=f"KC Works API token (default: ${TOKEN_ENV_VAR})",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"KC Works API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        help="attach this PDF instead of the cached build",
    )
    parser.add_argument(
        "--no-doi",
        action="store_true",
        help="omit the post's front-matter DOI from the record pids",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the record JSON without contacting KC Works",
    )
    args = parser.parse_args(argv)

    if args.dry_run:
        post = parse_post(args.post)
        slug = post_slug(args.post)
        record = build_metadata(
            post, canonical_url(slug), include_doi=not args.no_doi
        )
        print(json.dumps(record, indent=2))
        try:
            pdf = args.pdf or find_pdf(args.post.parent.parent, slug)
            print(f"Would attach: {args.post.name}, {pdf}", file=sys.stderr)
        except FileNotFoundError as exc:
            print(f"Warning: {exc}", file=sys.stderr)
        return 0

    if not args.token:
        print(
            f"No API token given: pass --token or set ${TOKEN_ENV_VAR}.",
            file=sys.stderr,
        )
        return 2

    client = KCWorksClient(args.base_url, args.token)
    try:
        result = upload_post(
            args.post,
            client,
            include_doi=not args.no_doi,
            pdf_path=args.pdf,
        )
    except (KCWorksError, FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Draft created: {result['id']}")
    print(f"Attached: {', '.join(result['files'])}")
    print(f"Review and publish at: {result['edit_url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
