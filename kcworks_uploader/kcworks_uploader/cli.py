"""Command-line entry point: upload one blog post to KC Works as a draft."""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from .client import KCWorksClient, KCWorksError
from .metadata import build_metadata
from .posts import (
    blog_collection,
    canonical_url,
    deposited_records,
    find_blog_root,
    find_pdf,
    parse_post,
    post_slug,
)

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
    parser.add_argument(
        "--collection",
        default=None,
        help=(
            "collection to include the published record in (default: "
            "kcworks_collection from the blog's _config.yml)"
        ),
    )
    parser.add_argument(
        "--no-collection",
        action="store_true",
        help="publish without including the record in any collection",
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

    collection = effective_collection(
        find_blog_root(Path.cwd()), args.collection, args.no_collection
    )
    if collection:
        try:
            resolved = client.get_collection(collection)["id"]
            status = include_in_collection(client, draft_id, resolved)
            print(f"Collection: {collection} ({status})")
        except KCWorksError as exc:
            # The record is published either way; the inclusion can be
            # retried with kcworks-collection backfill.
            print(f"Collection inclusion failed: {exc}", file=sys.stderr)
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


def collection_payload(slug: str, title: str, description: str = "") -> dict:
    """The community JSON for creating the blog's KC Works collection.

    review_policy "open" lets the collection's own curators publish into it
    without a review queue, so the uploader's inclusions complete directly.
    """
    payload = {
        "slug": slug,
        "access": {
            "visibility": "public",
            "member_policy": "closed",
            "record_policy": "closed",
            "review_policy": "open",
        },
        "metadata": {"title": title, "website": "https://eve.gd"},
    }
    if description:
        payload["metadata"]["description"] = description
    return payload


def include_in_collection(client, record_id: str, collection: str) -> str:
    """Put a published record into a collection (given its resolved id);
    returns 'included', 'already', or 'requested' (awaiting review).

    Inclusion raises a community-inclusion request; accepting it may fail
    when an open review policy has already auto-accepted, so the record's
    community membership is what finally decides the outcome.
    """
    result = client.add_to_collection(record_id, collection)
    processed = result.get("processed") or []
    if not processed:
        errors = result.get("errors") or []
        if any("already" in str(error).lower() for error in errors):
            return "already"
        raise KCWorksError(f"collection inclusion failed: {errors or result}")
    request_id = processed[0].get("request_id") or processed[0].get("request")
    if request_id:
        try:
            client.accept_request(request_id)
        except KCWorksError:
            pass
    record = client.get_record(record_id)
    ids = record.get("parent", {}).get("communities", {}).get("ids", [])
    return "included" if collection in ids else "requested"


def effective_collection(
    blog_root, override: str | None, disabled: bool
) -> str | None:
    """The collection to use: an explicit override, else the blog-wide
    _config.yml setting; None when disabled or nothing is configured."""
    if disabled:
        return None
    if override:
        return override
    if blog_root is None:
        return None
    return blog_collection(blog_root)


def collection_main(argv=None) -> int:
    """Entry point: create the blog collection / backfill deposits into it."""
    parser = argparse.ArgumentParser(
        prog="kcworks-collection",
        description=(
            "Create the blog's KC Works collection and backfill the "
            "deposits recorded in post front matter into it."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create", help="create the collection on KC Works")
    create.add_argument("--title", required=True, help="collection title")
    create.add_argument(
        "--slug",
        default=None,
        help="collection slug (default: kcworks_collection in _config.yml)",
    )
    create.add_argument("--description", default="")
    backfill = sub.add_parser(
        "backfill",
        help="include every post with a kcworks: deposit in the collection",
    )
    backfill.add_argument(
        "--posts-dir", type=Path, default=Path("_posts"),
        help="posts directory (default: _posts)",
    )
    backfill.add_argument(
        "--collection",
        default=None,
        help="collection slug (default: kcworks_collection in _config.yml)",
    )
    logo = sub.add_parser("logo", help="set the collection's logo image")
    logo.add_argument("image", type=Path, help="path to the logo image")
    logo.add_argument(
        "--collection",
        default=None,
        help="collection slug (default: kcworks_collection in _config.yml)",
    )
    for command in (create, backfill, logo):
        command.add_argument(
            "--token",
            default=os.environ.get(TOKEN_ENV_VAR),
            help=f"KC Works API token (default: ${TOKEN_ENV_VAR})",
        )
        command.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args(argv)

    if not args.token:
        print(
            f"No API token given: pass --token or set ${TOKEN_ENV_VAR}.",
            file=sys.stderr,
        )
        return 2

    blog_root = find_blog_root(Path.cwd())
    configured = blog_collection(blog_root) if blog_root else None
    client = KCWorksClient(args.base_url, args.token)

    if args.command == "create":
        slug = args.slug or configured
        if not slug:
            print(
                "No slug: pass --slug or set kcworks_collection in "
                "_config.yml.",
                file=sys.stderr,
            )
            return 2
        try:
            created = client.create_collection(
                collection_payload(slug, args.title, args.description)
            )
        except KCWorksError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        root = args.base_url.rstrip("/").removesuffix("/api")
        print(f"Collection created: {created['slug']}")
        print(f"View at: {root}/collections/{created['slug']}")
        return 0

    collection = args.collection or configured
    if not collection:
        print(
            "No collection: pass --collection or set kcworks_collection in "
            "_config.yml.",
            file=sys.stderr,
        )
        return 2
    try:
        collection_id = client.get_collection(collection)["id"]
    except KCWorksError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.command == "logo":
        if not args.image.is_file():
            print(f"No such image: {args.image}", file=sys.stderr)
            return 1
        try:
            client.upload_collection_logo(collection_id, args.image)
        except KCWorksError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        print(f"Logo set for {collection} from {args.image}")
        return 0

    failures = 0
    for path, record_id in deposited_records(args.posts_dir):
        try:
            status = include_in_collection(client, record_id, collection_id)
        except KCWorksError as exc:
            status = f"FAILED ({exc})"
            failures += 1
        print(f"{status:<10} {record_id}  {path.name}")
    return 1 if failures else 0


def upload_post(
    post_path: Path,
    client,
    include_doi: bool = True,
    pdf_path: Path | None = None,
    live: bool = False,
    collection: str | None = None,
) -> dict:
    """Create a KC Works draft for a post and attach its markdown and PDF.

    With live=True the draft is also published — and, when a collection is
    given, included in it (drafts leave inclusion for publish time).
    Returns {"id", "edit_url", "files", "record", "published"} plus
    "live_url" and "collection" when published.
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
        if collection:
            resolved = client.get_collection(collection)["id"]
            result["collection"] = include_in_collection(
                client, draft["id"], resolved
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
        "--collection",
        default=None,
        help=(
            "collection to include the published record in (default: "
            "kcworks_collection from the blog's _config.yml)"
        ),
    )
    parser.add_argument(
        "--no-collection",
        action="store_true",
        help="do not include the published record in any collection",
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
    collection = effective_collection(
        find_blog_root(Path(args.post).resolve().parent),
        args.collection,
        args.no_collection,
    )
    try:
        result = upload_post(
            args.post,
            client,
            include_doi=not args.no_doi,
            pdf_path=args.pdf,
            live=args.live,
            collection=collection,
        )
    except (KCWorksError, FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Draft created: {result['id']}")
    print(f"Attached: {', '.join(result['files'])}")
    if result["published"]:
        print(f"Published live at: {result['live_url']}")
        if result.get("collection"):
            print(f"Collection: {collection} ({result['collection']})")
    else:
        print(f"Review and publish at: {result['edit_url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
