"""Command-line entry points for BIROn deposits.

    biron-probe                     # check credentials, list collections
    biron-upload [--dry-run] POST   # deposit one post
    biron-backfill [--dry-run]      # deposit every post not yet in BIROn

Credentials come from BIRON_USERNAME and BIRON_PASSWORD (the .env file
via biron.sh). The deposit collection defaults to BIRON_COLLECTION or
the repository's SWORD inbox.
"""

import argparse
import os
import re
import sys
from pathlib import Path

import yaml
from kcworks_uploader.posts import (
    FRONT_MATTER_RE,
    canonical_url,
    find_pdf,
    parse_post,
    post_slug,
)

from .client import BASE_URL, PACKAGING, BironClient, BironError
from .ledger import load_ledger, prune_ledger, record_deposit
from .metadata import build_eprint_xml

LEDGER_PATH = "_biron/deposited.yml"
SKIP_PATH = "_biron/skip.yml"
MARKER_RE = re.compile(r"^biron:", re.MULTILINE)


def _has_marker(path: Path) -> bool:
    match = FRONT_MATTER_RE.match(path.read_text(encoding="utf-8"))
    return bool(match and MARKER_RE.search(match.group(1)))


def deposit_post(
    client,
    post_path: Path,
    collection_url: str,
    pdf_path: Path | None = None,
) -> dict:
    """Build the record for one post and deposit it.

    Attaches the built PDF edition and the markdown source. Returns the
    deposit receipt ``{"eprintid", "url"}``.
    """
    post_path = Path(post_path)
    post = parse_post(post_path)
    slug = post_slug(post_path)
    repo_root = post_path.parent.parent
    pdf = Path(pdf_path) if pdf_path else find_pdf(repo_root, slug)
    files = [
        (pdf.name, "application/pdf", pdf.read_bytes()),
        (post_path.name, "text/plain", post_path.read_bytes()),
    ]
    xml = build_eprint_xml(post, canonical_url(slug), files)
    return client.deposit(collection_url, xml)


def posts_to_deposit(repo_root: Path) -> list[Path]:
    """The posts that should go to BIROn and have not been sent.

    Every _posts/*.md file except those that already carry the biron:
    front-matter key, are pending in the deposited.yml ledger, or are
    listed in skip.yml.
    """
    repo_root = Path(repo_root)
    excluded = set(load_ledger(repo_root / LEDGER_PATH))
    skip_path = repo_root / SKIP_PATH
    if skip_path.exists():
        excluded.update(
            yaml.safe_load(skip_path.read_text(encoding="utf-8")) or []
        )
    return [
        path
        for path in sorted((repo_root / "_posts").glob("*.md"))
        if path.name not in excluded and not _has_marker(path)
    ]


def _client_from_env(base_url: str) -> BironClient:
    cookie = os.environ.get("BIRON_COOKIE")
    username = os.environ.get("BIRON_USERNAME")
    password = os.environ.get("BIRON_PASSWORD")
    if cookie:
        return BironClient(base_url=base_url, cookie=cookie)
    if username and password:
        return BironClient(username, password, base_url=base_url)
    sys.exit(
        "set BIRON_COOKIE (a logged-in browser session, e.g. "
        "'eprints_session=...') or BIRON_USERNAME/BIRON_PASSWORD in .env"
    )


def _resolve_collection(client, args, echo=print) -> str:
    """The deposit collection URL: explicit setting, else discovered.

    --collection and $BIRON_COLLECTION win; otherwise the service
    document's first collection accepting EPrints XML packaging is
    used (BIROn advertises /id/contents there), falling back to the
    CRUD endpoint when the service document is unreadable.
    """
    explicit = args.collection or os.environ.get("BIRON_COLLECTION")
    if explicit:
        return explicit
    fallback = f"{args.base_url.rstrip('/')}/id/contents"
    try:
        collections = client.service_document()
    except BironError as exc:
        echo(f"(service document unreadable, using {fallback}: {exc})")
        return fallback
    for collection in collections:
        if PACKAGING in collection["packaging"]:
            return collection["href"]
    return collections[0]["href"] if collections else fallback


def _common_args(parser):
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument(
        "--collection",
        help="SWORD collection URL (default: $BIRON_COLLECTION or the inbox)",
    )
    parser.add_argument("--dry-run", action="store_true")


def probe_main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check BIROn SWORD credentials and list deposit collections"
    )
    parser.add_argument("--base-url", default=BASE_URL)
    args = parser.parse_args(argv)
    client = _client_from_env(args.base_url)

    sword_ok = False
    try:
        collections = client.service_document()
    except BironError as exc:
        print(f"SWORD service document: FAILED ({exc})".rstrip())
    else:
        sword_ok = True
        print(f"SWORD authenticated against {args.base_url}. Collections:")
        for coll in collections:
            packaging = ", ".join(coll["packaging"]) or "(none listed)"
            print(f"  {coll['title']}: {coll['href']}")
            print(f"    packaging: {packaging}")

    status = client.contents_status()
    verdict = "usable" if status == 200 else "not usable"
    print(f"CRUD endpoint {args.base_url}/id/contents: HTTP {status} ({verdict})")
    if not sword_ok and status == 200:
        print(
            "SWORD is closed but CRUD accepts these credentials — set\n"
            f"  BIRON_COLLECTION={args.base_url}/id/contents\n"
            "in .env to deposit through it."
        )
    return 0 if sword_ok or status == 200 else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description="Deposit one post to BIROn")
    parser.add_argument("post", type=Path)
    parser.add_argument("--pdf", type=Path, help="attach this PDF instead")
    _common_args(parser)
    args = parser.parse_args(argv)

    slug = post_slug(args.post)
    if args.dry_run:
        explicit = args.collection or os.environ.get("BIRON_COLLECTION")
        collection = explicit or "(discovered from the service document)"
        post = parse_post(args.post)
        try:
            pdf = args.pdf or find_pdf(args.post.parent.parent, slug)
            pdf_note = str(pdf)
        except FileNotFoundError as exc:
            pdf_note = f"MISSING ({exc})"
        print(f"Would deposit to: {collection}")
        print(f"  title: {post.title}")
        print(f"  url: {canonical_url(slug)}")
        print(f"  doi: {post.doi or '(none)'}")
        print(f"  attachments: {args.post.name}, {pdf_note}")
        return 0

    client = _client_from_env(args.base_url)
    collection = _resolve_collection(client, args)
    receipt = deposit_post(client, args.post, collection, pdf_path=args.pdf)
    record_deposit(
        args.post.parent.parent / LEDGER_PATH, args.post.name, receipt["eprintid"]
    )
    print(f"Deposited: {receipt['url']} (awaiting review)")
    return 0


def backfill_main(argv=None):
    parser = argparse.ArgumentParser(
        description="Deposit every post that is not yet in BIROn"
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    _common_args(parser)
    args = parser.parse_args(argv)

    stamped = {
        path.name
        for path in (args.root / "_posts").glob("*.md")
        if _has_marker(path)
    }
    pruned = prune_ledger(args.root / LEDGER_PATH, stamped)
    if pruned:
        print(f"ledger: cleared {len(pruned)} now-live deposit(s)")

    pending = posts_to_deposit(args.root)
    if not pending:
        print("Nothing to deposit.")
        return 0
    if args.dry_run:
        print(f"Would deposit {len(pending)} post(s):")
        for path in pending:
            print(f"  {path.name}")
        return 0

    client = _client_from_env(args.base_url)
    collection = _resolve_collection(client, args)
    for path in pending:
        try:
            receipt = deposit_post(client, path, collection)
        except FileNotFoundError as exc:
            print(f"SKIPPED {path.name}: {exc}", file=sys.stderr)
            continue
        except BironError as exc:
            sys.exit(f"FAILED {path.name}: {exc}")
        record_deposit(args.root / LEDGER_PATH, path.name, receipt["eprintid"])
        print(f"deposited {path.name} -> {receipt['url']}")
    return 0
