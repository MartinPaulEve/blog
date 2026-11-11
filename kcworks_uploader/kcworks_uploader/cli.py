"""Command-line entry points: deposit blog posts in KC Works.

Deposits use the streamlined import API, which creates, attaches files
to, publishes and collects a work in a single request. Publishing a
hand-made draft and managing the collection still go through the
ordinary records and communities endpoints.
"""

import argparse
import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

import yaml

from .client import KCWorksClient, KCWorksConflict, KCWorksError
from .metadata import build_metadata
from .posts import (
    FRONT_MATTER_RE,
    blog_collection,
    canonical_url,
    deposited_records,
    find_blog_root,
    find_pdf,
    parse_post,
    pending_posts,
    post_slug,
    record_deposit,
    update_deposit,
)

DEFAULT_BASE_URL = "https://works.hcommons.org/api"
TOKEN_ENV_VAR = "KCWORKS_API_TOKEN"
NO_COLLECTION = (
    "No collection: the import API deposits into a collection, so pass "
    "--collection or set kcworks_collection in the blog's _config.yml."
)


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


def _no_token() -> int:
    print(
        f"No API token given: pass --token or set ${TOKEN_ENV_VAR}.",
        file=sys.stderr,
    )
    return 2


def _add_token_and_base(parser, base_help=None) -> None:
    parser.add_argument(
        "--token",
        default=os.environ.get(TOKEN_ENV_VAR),
        help=f"KC Works API token (default: ${TOKEN_ENV_VAR})",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=base_help or f"KC Works API base URL (default: {DEFAULT_BASE_URL})",
    )


def _add_collection_option(parser) -> None:
    parser.add_argument(
        "--collection",
        default=None,
        help=(
            "collection to import into (default: kcworks_collection from "
            "the blog's _config.yml)"
        ),
    )


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
        return _no_token()

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


def collection_payload(slug: str, title: str, description: str = "") -> dict:
    """The community JSON for creating the blog's KC Works collection.

    review_policy "open" lets the collection's own curators publish into it
    without a review queue, so the uploader's imports complete directly.
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
        _add_token_and_base(command)
    args = parser.parse_args(argv)

    if not args.token:
        return _no_token()

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


def _post_files(post_path: Path, pdf_path: Path | None = None) -> list[Path]:
    """The files deposited for a post: its markdown source and PDF edition."""
    post_path = Path(post_path)
    if pdf_path is not None:
        pdf = Path(pdf_path)
    else:
        pdf = find_pdf(post_path.parent.parent, post_slug(post_path))
    return [post_path, pdf]


def _post_record(post_path: Path, files: list[Path], include_doi: bool) -> dict:
    post_path = Path(post_path)
    slug = post_slug(post_path)
    return build_metadata(
        parse_post(post_path),
        canonical_url(slug),
        include_doi=include_doi,
        files=files,
        source_id=slug,
    )


def _import(client, collection: str, record: dict, files: list[Path]) -> dict:
    """Import one work; shape the outcome as {"id", "live_url", "files",
    "record", "collection", "existing"}.

    A 409 that names the existing work (its Location) is treated as a
    deposit that already happened, so callers can record it; one without
    a Location is an error.
    """
    try:
        imported = client.import_work(collection, record, files)
    except KCWorksConflict as exc:
        if not exc.location:
            raise
        return {
            "id": draft_id_from_url(exc.location),
            "live_url": exc.location,
            "files": [],
            "record": {},
            "collection": collection,
            "existing": True,
        }
    return {
        "id": imported["record_id"],
        "live_url": imported.get("record_url")
        or _live_url(client.base_url, imported["record_id"], {}),
        "files": [
            path.name
            for path in files
            if path.name in (imported.get("files") or {})
        ]
        or [path.name for path in files],
        "record": imported.get("metadata") or {},
        "collection": imported.get("collection_id") or collection,
        "existing": False,
    }


def upload_post(
    post_path: Path,
    client,
    collection: str,
    include_doi: bool = True,
    pdf_path: Path | None = None,
) -> dict:
    """Deposit a post in KC Works: one import request creates the work,
    attaches the markdown source and PDF edition, publishes it and
    places it in the collection.

    Returns {"id", "live_url", "files", "record", "collection",
    "existing"}; existing is True when KC Works reported the work was
    already there (and live_url is that work).
    """
    files = _post_files(post_path, pdf_path)
    record = _post_record(post_path, files, include_doi)
    return _import(client, collection, record, files)


def backfill_main(argv=None) -> int:
    """Entry point: deposit and publish every post not yet in KC Works.

    Works through every post without a kcworks: front-matter record,
    importing each (with its markdown and PDF) straight into the
    configured collection, stamping the new record URL back into the
    post, and appending a JSON line per outcome to the log so failures
    can be reviewed afterwards. Waits --delay seconds between deposits
    to stay within the server's rate limits. Re-running resumes
    automatically: stamped posts are no longer pending.
    """
    parser = argparse.ArgumentParser(
        prog="kcworks-backfill",
        description=(
            "Deposit and publish every blog post that is not yet in "
            "KC Works, logging each outcome."
        ),
    )
    parser.add_argument(
        "--posts-dir",
        type=Path,
        default=Path("_posts"),
        help="posts directory (default: _posts)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="deposit at most this many posts (default: all pending)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=10.0,
        help="seconds to wait between deposits (default: 10)",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=Path("kcworks-backfill.log"),
        help=(
            "JSON-lines log appended with every outcome "
            "(default: kcworks-backfill.log)"
        ),
    )
    _add_token_and_base(parser)
    _add_collection_option(parser)
    parser.add_argument(
        "--no-doi",
        action="store_true",
        help="omit the posts' front-matter DOIs from the record pids",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="list the pending posts without contacting KC Works",
    )
    args = parser.parse_args(argv)

    pending = pending_posts(args.posts_dir)
    if args.limit is not None:
        pending = pending[: args.limit]

    if args.dry_run:
        for path in pending:
            print(path.name)
        print(f"{len(pending)} post(s) pending deposit")
        return 0
    if not pending:
        print("Nothing to deposit: every post has a kcworks: record.")
        return 0
    if not args.token:
        return _no_token()
    collection = effective_collection(
        find_blog_root(Path.cwd()), args.collection, False
    )
    if not collection:
        print(NO_COLLECTION, file=sys.stderr)
        return 2

    client = KCWorksClient(args.base_url, args.token)
    total = len(pending)
    published = existing = 0
    failures: list[tuple[str, str]] = []
    interrupted = False
    try:
        for index, path in enumerate(pending, start=1):
            entry = {"time": _utc_now(), "post": path.name}
            try:
                result = upload_post(
                    path, client, collection, include_doi=not args.no_doi
                )
            except (KCWorksError, FileNotFoundError, ValueError) as exc:
                failures.append((path.name, str(exc)))
                entry.update(status="failed", error=str(exc))
                print(f"[{index}/{total}] FAILED    {path.name}: {exc}")
            else:
                record_deposit(path, result["live_url"])
                status = "existing" if result["existing"] else "published"
                if result["existing"]:
                    existing += 1
                else:
                    published += 1
                entry.update(
                    status=status,
                    id=result["id"],
                    live_url=result["live_url"],
                    collection=result["collection"],
                )
                print(
                    f"[{index}/{total}] {status:<9} {path.name} "
                    f"-> {result['live_url']}"
                )
            _append_log(args.log, entry)
            if index < total:
                time.sleep(args.delay)
    except KeyboardInterrupt:
        interrupted = True
        print("\nInterrupted; the log records everything deposited so far.")

    print(
        f"\nDone: {published} published, {len(failures)} failed"
        + (f", {existing} already in KC Works" if existing else "")
    )
    if failures:
        print("Failed posts:")
        for name, error in failures:
            print(f"  {name}: {error}")
        print("Re-run the backfill to retry them.")
    print(f"Log: {args.log}")
    if interrupted:
        return 130
    return 1 if failures else 0


def needs_update(record: dict, last_modified: str) -> bool:
    """Whether a deposit predates the post's last modification.

    Compares dates only (the repository's updated stamp is a datetime);
    a record whose state is unknown counts as needing an update.
    """
    updated = str(record.get("updated") or "")[:10]
    if not updated:
        return True
    return updated < str(last_modified)[:10]


def update_post(post_path: Path, client, collection: str) -> dict:
    """Bring a post's KC Works deposit up to date with fresh files.

    Re-imports the post with the same DOI pid and import-recid
    identifier as its original deposit: the import API matches the
    existing work on those, applies the changed metadata and reconciles
    the attached files against the current markdown and PDF. Returns
    {"id", "live_url", "record"} for the work KC Works reports back
    (which may differ from the stamped record if an earlier version
    carried the DOI).
    """
    files = _post_files(post_path)
    record = _post_record(post_path, files, include_doi=True)
    result = _import(client, collection, record, files)
    if result["existing"]:
        raise KCWorksError(
            f"KC Works refused to update the existing work at "
            f"{result['live_url']}"
        )
    return result


def _kcworks_url(post_path: Path) -> str | None:
    match = FRONT_MATTER_RE.match(Path(post_path).read_text(encoding="utf-8"))
    if not match:
        return None
    value = (yaml.safe_load(match.group(1)) or {}).get("kcworks")
    return str(value) if value else None


def update_main(argv=None) -> int:
    """Entry point: refresh the deposits of modified posts."""
    parser = argparse.ArgumentParser(
        prog="kcworks-update",
        description=(
            "Re-import the KC Works deposit for posts whose "
            "last_modified_at postdates the deposited record, so the "
            "work carries the current metadata, markdown and PDF."
        ),
    )
    parser.add_argument(
        "posts", nargs="*", type=Path,
        help="post files (default: every post with kcworks: and last_modified_at)",
    )
    parser.add_argument(
        "--posts-dir", type=Path, default=Path("_posts"),
        help="posts directory scanned when no posts are given",
    )
    parser.add_argument(
        "--delay", type=float, default=10.0,
        help="seconds between updates (default: 10)",
    )
    parser.add_argument(
        "--log", type=Path, default=Path("kcworks-update.log"),
        help="JSON-lines log (default: kcworks-update.log)",
    )
    _add_token_and_base(parser)
    _add_collection_option(parser)
    parser.add_argument(
        "--dry-run", action="store_true",
        help="list candidate posts without contacting KC Works",
    )
    args = parser.parse_args(argv)

    candidates = []
    paths = args.posts or sorted(Path(args.posts_dir).glob("*.md"))
    for path in paths:
        post = parse_post(path)
        url = _kcworks_url(path)
        if url and post.last_modified:
            candidates.append((Path(path), url, post.last_modified))

    if args.dry_run:
        for path, url, modified in candidates:
            print(f"{path.name}: modified {modified}, deposit {url}")
        print(f"{len(candidates)} candidate post(s)")
        return 0
    if not candidates:
        print("Nothing to update: no post has both kcworks: and last_modified_at.")
        return 0
    if not args.token:
        return _no_token()
    collection = effective_collection(
        find_blog_root(Path.cwd()), args.collection, False
    )
    if not collection:
        print(NO_COLLECTION, file=sys.stderr)
        return 2

    client = KCWorksClient(args.base_url, args.token)
    total = len(candidates)
    updated = skipped = 0
    failures: list[tuple[str, str]] = []
    for index, (path, url, modified) in enumerate(candidates, start=1):
        entry = {"time": _utc_now(), "post": path.name}
        try:
            record = client.get_record(draft_id_from_url(url))
            if not needs_update(record, modified):
                skipped += 1
                entry.update(status="fresh")
                print(f"[{index}/{total}] fresh     {path.name}")
                continue
            result = update_post(path, client, collection)
        except (KCWorksError, FileNotFoundError, ValueError) as exc:
            failures.append((path.name, str(exc)))
            entry.update(status="failed", error=str(exc))
            print(f"[{index}/{total}] FAILED    {path.name}: {exc}")
        else:
            update_deposit(path, result["live_url"])
            updated += 1
            entry.update(
                status="updated", id=result["id"], live_url=result["live_url"]
            )
            print(f"[{index}/{total}] updated   {path.name} -> {result['live_url']}")
        finally:
            _append_log(args.log, entry)
        if index < total:
            time.sleep(args.delay)

    print(f"\nDone: {updated} updated, {skipped} fresh, {len(failures)} failed")
    if failures:
        for name, error in failures:
            print(f"  {name}: {error}")
    return 1 if failures else 0


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _append_log(log_path: Path, entry: dict) -> None:
    with Path(log_path).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="kcworks-upload",
        description=(
            "Deposit a blog post in KC Works: one import request creates "
            "the work with the markdown source and built PDF edition "
            "attached, publishes it and places it in the blog collection."
        ),
    )
    parser.add_argument("post", type=Path, help="path to the _posts/*.md file")
    _add_token_and_base(parser)
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
        help=argparse.SUPPRESS,  # imports always publish; kept for old scripts
    )
    _add_collection_option(parser)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the record JSON without contacting KC Works",
    )
    args = parser.parse_args(argv)

    if args.dry_run:
        try:
            files = _post_files(args.post, args.pdf)
            note = "Would attach: " + ", ".join(str(f) for f in files)
        except FileNotFoundError as exc:
            files = [Path(args.post)]
            note = f"Warning: {exc}"
        record = _post_record(args.post, files, include_doi=not args.no_doi)
        print(json.dumps(record, indent=2))
        print(note, file=sys.stderr)
        return 0

    if not args.token:
        return _no_token()
    collection = effective_collection(
        find_blog_root(Path(args.post).resolve().parent), args.collection, False
    )
    if not collection:
        print(NO_COLLECTION, file=sys.stderr)
        return 2

    client = KCWorksClient(args.base_url, args.token)
    try:
        result = upload_post(
            args.post,
            client,
            collection,
            include_doi=not args.no_doi,
            pdf_path=args.pdf,
        )
    except (KCWorksError, FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if result["existing"]:
        print(f"Already in KC Works: {result['live_url']}")
    else:
        print(f"Imported: {result['id']}")
        print(f"Attached: {', '.join(result['files'])}")
        print(f"Published live at: {result['live_url']}")
        print(f"Collection: {collection} ({result['collection']})")
    record_deposit(args.post, result["live_url"])
    print("Recorded kcworks: in the post's front matter.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
