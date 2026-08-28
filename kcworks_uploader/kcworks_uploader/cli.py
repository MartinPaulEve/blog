"""Command-line entry point: upload one blog post to KC Works as a draft."""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from .client import KCWorksClient, KCWorksError
from .metadata import build_metadata
from .posts import canonical_url, find_pdf, parse_post, post_slug

DEFAULT_BASE_URL = "https://works.hcommons.org/api"
TOKEN_ENV_VAR = "KCWORKS_API_TOKEN"


def draft_id_from_url(value: str) -> str:
    """The record id from a draft/record URL, or the value itself if bare."""
    value = value.strip()
    if "://" not in value:
        return value.rstrip("/")
    segments = [s for s in urlparse(value).path.split("/") if s]
    if not segments:
        raise ValueError(f"No record id found in {value!r}")
    return segments[-1]


def api_base_from_url(value: str) -> str | None:
    """The API base implied by a KC Works URL; None for a bare record id."""
    if "://" not in value:
        return None
    parsed = urlparse(value)
    return f"{parsed.scheme}://{parsed.netloc}/api"


def publish_main(argv=None) -> int:
    """Entry point: publish an existing KC Works draft by URL or id."""
    parser = argparse.ArgumentParser(
        prog="kcworks-publish",
        description="Publish an existing KC Works draft, making it live.",
    )
    parser.add_argument(
        "draft",
        help=(
            "draft URL (e.g. https://works.hcommons.org/uploads/<id>) "
            "or bare record id"
        ),
    )
    parser.add_argument(
        "--token",
        default=os.environ.get(TOKEN_ENV_VAR),
        help=f"KC Works API token (default: ${TOKEN_ENV_VAR})",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help=(
            "KC Works API base URL (default: derived from the draft URL, "
            f"else {DEFAULT_BASE_URL})"
        ),
    )
    args = parser.parse_args(argv)

    if not args.token:
        print(
            f"No API token given: pass --token or set ${TOKEN_ENV_VAR}.",
            file=sys.stderr,
        )
        return 2

    draft_id = draft_id_from_url(args.draft)
    base_url = (
        args.base_url or api_base_from_url(args.draft) or DEFAULT_BASE_URL
    )
    client = KCWorksClient(base_url, args.token)
    try:
        published = client.publish_draft(draft_id)
    except KCWorksError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Published: {draft_id}")
    print(f"Live at: {_live_url(base_url, draft_id, published)}")
    return 0


def _live_url(base_url: str, record_id: str, published: dict) -> str:
    from_links = published.get("links", {}).get("self_html")
    if from_links:
        return from_links
    root = base_url.rstrip("/").removesuffix("/api")
    return f"{root}/records/{record_id}"


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
    live: bool = False,
) -> dict:
    """Create a KC Works draft for a post and attach its markdown and PDF.

    With live=True the draft is also published. Returns {"id", "edit_url",
    "files", "record", "published"} plus "live_url" when published.
    """
    post_path = Path(post_path)
    post = parse_post(post_path)
    slug = post_slug(post_path)
    if pdf_path is not None:
        pdf = Path(pdf_path)
    else:
        pdf = find_pdf(post_path.parent.parent, slug)
    record = build_metadata(
        post,
        canonical_url(slug),
        include_doi=include_doi,
        pdf_filename=pdf.name,
    )

    draft = client.create_draft(record)
    files = client.upload_files(draft["id"], [post_path, pdf])
    # Re-assert files.default_preview now the PDF exists on the draft; the
    # server ignores it during creation, when there are no files yet.
    updated = client.update_draft(draft["id"], record)
    result = {
        "id": draft["id"],
        "edit_url": deposit_url(client.base_url, draft["id"]),
        "files": files,
        "record": updated,
        "published": False,
    }
    if live:
        published = client.publish_draft(draft["id"])
        result["record"] = published
        result["published"] = True
        result["live_url"] = _live_url(
            client.base_url, draft["id"], published
        )
    return result


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
        "--live",
        action="store_true",
        help="publish immediately instead of leaving a draft for review",
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
        try:
            pdf = args.pdf or find_pdf(args.post.parent.parent, slug)
            pdf_note = f"Would attach: {args.post.name}, {pdf}"
        except FileNotFoundError as exc:
            pdf = Path(f"{slug}.pdf")
            pdf_note = f"Warning: {exc}"
        record = build_metadata(
            post,
            canonical_url(slug),
            include_doi=not args.no_doi,
            pdf_filename=pdf.name,
        )
        print(json.dumps(record, indent=2))
        print(pdf_note, file=sys.stderr)
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
            live=args.live,
        )
    except (KCWorksError, FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Draft created: {result['id']}")
    print(f"Attached: {', '.join(result['files'])}")
    if result["published"]:
        print(f"Published live at: {result['live_url']}")
    else:
        print(f"Review and publish at: {result['edit_url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
