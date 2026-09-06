"""Command-line entry point: upload one blog post to KC Works as a draft."""

import argparse
import json
import os
import sys
import time
from datetime import UTC, datetime
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
    pending_posts,
    post_slug,
    record_deposit,
    update_deposit,
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


def backfill_main(argv=None) -> int:
    """Entry point: deposit and publish every post not yet in KC Works.

    Works through every post without a kcworks: front-matter record,
    publishing each (with its markdown and PDF) into the configured
    collection, stamping the new record URL back into the post, and
    appending a JSON line per outcome to the log so failures can be
    reviewed afterwards. Waits --delay seconds between deposits to stay
    within the server's rate limits. Re-running resumes automatically:
    stamped posts are no longer pending.
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
    parser.add_argument(
        "--token",
        default=os.environ.get(TOKEN_ENV_VAR),
        help=f"KC Works API token (default: ${TOKEN_ENV_VAR})",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--collection",
        default=None,
        help=(
            "collection to include published records in (default: "
            "kcworks_collection from the blog's _config.yml)"
        ),
    )
    parser.add_argument(
        "--no-collection",
        action="store_true",
        help="publish without including the records in any collection",
    )
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
        print(
            f"No API token given: pass --token or set ${TOKEN_ENV_VAR}.",
            file=sys.stderr,
        )
        return 2

    client = KCWorksClient(args.base_url, args.token)
    collection = effective_collection(
        find_blog_root(Path.cwd()), args.collection, args.no_collection
    )
    collection_id = None
    if collection:
        try:
            collection_id = client.get_collection(collection)["id"]
        except KCWorksError as exc:
            print(
                f"Cannot resolve collection {collection!r}: {exc}",
                file=sys.stderr,
            )
            return 2

    total = len(pending)
    published = 0
    failures: list[tuple[str, str]] = []
    inclusion_failures = 0
    interrupted = False
    try:
        for index, path in enumerate(pending, start=1):
            entry = {"time": _utc_now(), "post": path.name}
            try:
                result = upload_post(
                    path, client, include_doi=not args.no_doi, live=True
                )
            except (KCWorksError, FileNotFoundError, ValueError) as exc:
                failures.append((path.name, str(exc)))
                entry.update(status="failed", error=str(exc))
                print(f"[{index}/{total}] FAILED    {path.name}: {exc}")
            else:
                record_deposit(path, result["live_url"])
                published += 1
                entry.update(
                    status="published",
                    id=result["id"],
                    live_url=result["live_url"],
                )
                if collection_id:
                    try:
                        entry["collection"] = include_in_collection(
                            client, result["id"], collection_id
                        )
                    except KCWorksError as exc:
                        inclusion_failures += 1
                        entry["collection"] = f"failed: {exc}"
                print(
                    f"[{index}/{total}] published {path.name} "
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
        + (
            f", {inclusion_failures} collection inclusion(s) failed"
            if inclusion_failures
            else ""
        )
    )
    if failures:
        print("Failed posts:")
        for name, error in failures:
            print(f"  {name}: {error}")
        print("Re-run the backfill to retry them.")
    if inclusion_failures:
        print(
            "Retry the failed inclusions with: "
            "./kcworks.sh collection backfill"
        )
    print(f"Log: {args.log}")
    if interrupted:
        return 130
    return 1 if failures or inclusion_failures else 0


def needs_update(record: dict, last_modified: str) -> bool:
    """Whether a deposit predates the post's last modification.

    Compares dates only (the repository's updated stamp is a datetime);
    a record whose state is unknown counts as needing an update.
    """
    updated = str(record.get("updated") or "")[:10]
    if not updated:
        return True
    return updated < str(last_modified)[:10]


def update_post(post_path: Path, client) -> dict:
    """Publish a new version of a post's KC Works deposit with fresh files.

    Creates a new-version draft of the record in the post's kcworks:
    entry, re-derives the record metadata — asking KC Works to mint a
    managed DOI for the version, since the post's own external DOI
    belongs to the original and cannot be reused — uploads the current
    markdown and PDF, publishes, and returns {"id", "live_url",
    "record"}.
    """
    post_path = Path(post_path)
    post = parse_post(post_path)
    slug = post_slug(post_path)
    pdf = find_pdf(post_path.parent.parent, slug)
    record = build_metadata(
        post,
        canonical_url(slug),
        include_doi=False,
        pdf_filename=pdf.name,
    )

    url = _kcworks_url(post_path)
    if not url:
        raise ValueError(f"{post_path} has no kcworks: deposit to version")
    draft = client.new_version(draft_id_from_url(url))
    # KC Works requires a DOI with a concrete identifier on every
    # published record, and an external DOI cannot be reused across
    # versions (the post's own DOI stays on the original) — so reserve a
    # KC Works-minted DOI on the draft, unless a retry finds one already
    # reserved, and carry it through every subsequent draft update.
    pids = draft.get("pids") or {}
    doi = pids.get("doi") or {}
    if doi.get("identifier") and doi.get("provider") != "external":
        record["pids"] = pids  # a prior run's reservation: keep it
    else:
        # Draft PUTs are lenient, so failed runs can leave a malformed or
        # external doi pid behind; it blocks reservation until removed.
        # Schema-only debris has no PID row, making the delete endpoint
        # 404 — clearing pids by (lenient) PUT covers that case.
        if doi:
            try:
                client.delete_draft_pid(draft["id"], "doi")
            except KCWorksError:
                pass
            record["pids"] = {}
            client.update_draft(draft["id"], record)
        reserved = client.reserve_doi(draft["id"])
        record["pids"] = reserved.get("pids") or {}
    client.update_draft(draft["id"], record)
    # A retry after a failed publish finds files already on the draft;
    # upload only what is missing.
    existing = {entry.get("key") for entry in client.list_draft_files(draft["id"])}
    missing = [p for p in (post_path, pdf) if p.name not in existing]
    if missing:
        client.upload_files(draft["id"], missing)
    client.update_draft(draft["id"], record)
    published = client.publish_draft(draft["id"])
    return {
        "id": draft["id"],
        "live_url": _live_url(client.base_url, draft["id"], published),
        "record": published,
    }


def _kcworks_url(post_path: Path) -> str | None:
    import yaml

    from .posts import FRONT_MATTER_RE

    match = FRONT_MATTER_RE.match(Path(post_path).read_text(encoding="utf-8"))
    if not match:
        return None
    value = (yaml.safe_load(match.group(1)) or {}).get("kcworks")
    return str(value) if value else None


def update_main(argv=None) -> int:
    """Entry point: publish new deposit versions for modified posts."""
    parser = argparse.ArgumentParser(
        prog="kcworks-update",
        description=(
            "Publish a new version of the KC Works deposit for posts whose "
            "last_modified_at postdates the deposited record, attaching the "
            "current markdown and PDF."
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
    parser.add_argument(
        "--token",
        default=os.environ.get(TOKEN_ENV_VAR),
        help=f"KC Works API token (default: ${TOKEN_ENV_VAR})",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
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
        print(
            f"No API token given: pass --token or set ${TOKEN_ENV_VAR}.",
            file=sys.stderr,
        )
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
            result = update_post(path, client)
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
        record_deposit(args.post, result["live_url"])
        print("Recorded kcworks: in the post's front matter.")
        if result.get("collection"):
            print(f"Collection: {collection} ({result['collection']})")
    else:
        print(f"Review and publish at: {result['edit_url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
