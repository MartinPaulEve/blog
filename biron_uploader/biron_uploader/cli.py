"""Command-line entry points for BIROn deposits.

    biron-probe                     # check credentials, list collections
    biron-upload [--dry-run] POST   # deposit one post
    biron-backfill [--dry-run]      # deposit every post not yet in BIROn
    biron-update [--dry-run]        # refresh records of changed posts
    biron-pending                   # what the next deploy would send
    biron-session                   # make sure a session is on file first

Credentials come from BIRON_USERNAME and BIRON_PASSWORD (the .env file
via biron.sh). The deposit collection defaults to BIRON_COLLECTION or
the repository's SWORD inbox.
"""

import argparse
import importlib.util
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

from . import cookiejar
from .client import BASE_URL, PACKAGING, BironClient, BironError
from .ledger import (
    file_digest,
    load_ledger,
    load_shipped,
    prune_ledger,
    record_deposit,
    record_shipped,
)
from .metadata import build_document_xml, build_eprint_xml

LEDGER_PATH = "_biron/deposited.yml"
SHIPPED_PATH = "_biron/shipped.yml"
SKIP_PATH = "_biron/skip.yml"
MARKER_RE = re.compile(r"^biron:", re.MULTILINE)
BIRON_LINK_RE = re.compile(r"^biron:\s*\S*?/(\d+)/?\s*$", re.MULTILINE)


def _has_marker(path: Path) -> bool:
    match = FRONT_MATTER_RE.match(path.read_text(encoding="utf-8"))
    return bool(match and MARKER_RE.search(match.group(1)))


def _build_payload(post_path: Path, pdf_path: Path | None = None):
    """The (metadata XML, documents) for one post's record."""
    post_path = Path(post_path)
    post = parse_post(post_path)
    slug = post_slug(post_path)
    repo_root = post_path.parent.parent
    pdf = Path(pdf_path) if pdf_path else find_pdf(repo_root, slug)
    files = [
        (pdf.name, "application/pdf", pdf.read_bytes()),
        (post_path.name, "text/plain", post_path.read_bytes()),
    ]
    xml = build_eprint_xml(post, canonical_url(slug), status="archive")
    documents = [
        {
            "xml": build_document_xml(filename, mime, placement),
            "filename": filename,
            "mime": mime,
            "data": data,
        }
        for placement, (filename, mime, data) in enumerate(files, 1)
    ]
    return xml, documents


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
    xml, documents = _build_payload(post_path, pdf_path)
    return client.deposit(
        collection_url, xml, documents=documents, make_live=True
    )


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


def _resolve_cookie(root: Path) -> tuple[str | None, str | None]:
    """The session cookie and its source ("env" or "file").

    An explicit BIRON_COOKIE value wins; "auto"/"browser" (or no
    setting) defers to the harvested .biron_cookie file.
    """
    env = (os.environ.get("BIRON_COOKIE") or "").strip()
    if env and env.lower() not in ("auto", "browser"):
        return env, "env"
    file_cookie = cookiejar.read_cookie_file(root)
    if file_cookie:
        return file_cookie, "file"
    return None, None


def _ensure_client(base_url: str, root: Path, echo=print) -> BironClient:
    """A client with working credentials, refreshing the cookie if stale.

    Cookie-based sessions are verified against /id/contents; a stale
    harvested cookie triggers a silent headless re-login through the
    dedicated browser profile — unless BIRON_NO_BROWSER is set (a remote
    build host, where the cookie arrives from the caller and nobody could
    see a sign-in window), which turns a stale session into a clear
    failure instead. Basic credentials are used as-is.
    """
    cookie, source = _resolve_cookie(root)
    username = os.environ.get("BIRON_USERNAME")
    password = os.environ.get("BIRON_PASSWORD")

    if cookie:
        client = BironClient(base_url=base_url, cookie=cookie)
        if client.contents_status() == 200:
            return client
        if source == "env":
            sys.exit(
                "the BIRON_COOKIE in .env is stale — replace it, or set "
                "BIRON_COOKIE=auto and run ./biron.sh login"
            )
        echo("BIROn session stale; refreshing through the browser profile…")
    elif username and password:
        return BironClient(username, password, base_url=base_url)
    else:
        echo("No BIROn session on file; attempting a headless login…")

    if os.environ.get("BIRON_NO_BROWSER"):
        sys.exit(
            "BIROn session missing or stale and no browser may be opened "
            "here (BIRON_NO_BROWSER) — run ./biron.sh login on the machine "
            "that starts the deploy, which ships the cookie to this host"
        )
    try:
        cookie = cookiejar.harvest(root, headless=True, echo=echo)
    except cookiejar.LoginError as exc:
        sys.exit(f"BIROn login needed: {exc}")
    client = BironClient(base_url=base_url, cookie=cookie)
    if client.contents_status() != 200:
        sys.exit(
            "the freshly harvested session was rejected — run "
            "./biron.sh login and sign in interactively"
        )
    return client


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


def _biron_eprintid(path: Path) -> int | None:
    """The eprint id from a post's biron: front-matter link, if any."""
    match = FRONT_MATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        return None
    link = BIRON_LINK_RE.search(match.group(1))
    return int(link.group(1)) if link else None


def stale_posts(root: Path) -> tuple[list, list]:
    """Deposited posts the shipped ledger has not seen, and those changed.

    Returns ``(baselined, stale)``: ``baselined`` pairs each post the
    ledger does not know with its current digest (its record is assumed
    current); ``stale`` pairs each post whose digest differs from the
    ledger with its eprintid (its record needs replacing).
    """
    root = Path(root)
    shipped = load_shipped(root / SHIPPED_PATH)
    baselined, stale = [], []
    for path in sorted((root / "_posts").glob("*.md")):
        eprintid = _biron_eprintid(path)
        if eprintid is None:
            continue
        digest = file_digest(path)
        if path.name not in shipped:
            baselined.append((path, digest))
        elif shipped[path.name] != digest:
            stale.append((path, eprintid))
    return baselined, stale


def update_main(argv=None):
    """Refresh BIROn records for posts changed since their deposit.

    EPrints has no versioning, so a changed post's record is replaced
    in place (same eprintid, same URL). Staleness is detected against
    the shipped-content ledger; deposited posts the ledger has never
    seen (the pre-pipeline backlog) are baselined as current rather
    than blindly rewritten.
    """
    parser = argparse.ArgumentParser(
        description="Refresh BIROn records for posts changed since deposit"
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    _common_args(parser)
    args = parser.parse_args(argv)

    shipped_path = args.root / SHIPPED_PATH
    baselined, stale = stale_posts(args.root)

    if args.dry_run:
        print(
            f"Would baseline {len(baselined)} post(s); "
            f"would update {len(stale)}:"
        )
        for path, eprintid in stale:
            print(f"  {path.name} -> eprint {eprintid}")
        return 0

    for path, digest in baselined:
        record_shipped(shipped_path, path.name, digest)
    if baselined:
        print(
            f"baselined {len(baselined)} post(s) "
            "(existing records assumed current)"
        )
    if not stale:
        if not baselined:
            print("Nothing to update.")
        return 0

    client = _ensure_client(args.base_url, args.root)
    for path, eprintid in stale:
        try:
            xml, documents = _build_payload(path)
            receipt = client.update(eprintid, xml, documents=documents)
        except FileNotFoundError as exc:
            print(f"SKIPPED {path.name}: {exc}", file=sys.stderr)
            continue
        except BironError as exc:
            sys.exit(f"FAILED {path.name}: {exc}")
        record_shipped(shipped_path, path.name, file_digest(path))
        print(f"updated {path.name} -> {receipt['url']}")
    return 0


EXIT_SKIPPED = 3


def pending_work(root: Path) -> dict:
    """What the next deploy would send to BIROn, without touching the network.

    ``deposit`` lists the posts backfill would create records for;
    ``update`` the (post, eprintid) pairs whose records update would
    replace. Both are decided from the working tree and the ledgers
    alone, so this is safe to ask before any sign-in.
    """
    root = Path(root)
    _, stale = stale_posts(root)
    return {"deposit": posts_to_deposit(root), "update": stale}


def _report_pending(work: dict) -> None:
    if work["deposit"]:
        print(f"Would deposit {len(work['deposit'])} post(s):")
        for path in work["deposit"]:
            print(f"  {path.name}")
    if work["update"]:
        print(f"Would update {len(work['update'])} record(s):")
        for path, eprintid in work["update"]:
            print(f"  {path.name} -> eprint {eprintid}")


def pending_main(argv=None):
    """List pending BIROn work; exit 0 when there is any, 1 when there is none."""
    parser = argparse.ArgumentParser(
        description="List what the next deploy would send to BIROn "
        "(exit 0 if anything, 1 if nothing)"
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    work = pending_work(args.root)
    if not (work["deposit"] or work["update"]):
        print("Nothing pending for BIROn.")
        return 1
    _report_pending(work)
    return 0


def _cookie_works(base_url: str, cookie: str) -> bool:
    return BironClient(base_url=base_url, cookie=cookie).contents_status() == 200


def session_main(argv=None):
    """Make sure a usable BIROn session is on file if the deploy will need one.

    The one call a deploy makes before handing off to a build host that
    cannot open a browser. In order: nothing pending means no session
    is needed (exit 0 at once, no network); Basic credentials need no
    cookie; a cookie that BIROn still accepts is kept; a stale or
    missing one is renewed silently through the persisted browser
    profile; only when that fails does the sign-in window open — where
    pressing C abandons it (exit EXIT_SKIPPED, 3) so the deploy can
    carry on without BIROn. Any other failure exits 1. BIRON_NO_BROWSER
    forbids both browser runs, as on a build host.
    """
    parser = argparse.ArgumentParser(
        description="Ensure a BIROn session is on file when the deploy "
        "has something to send"
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--timeout", type=float, default=None,
                        help="seconds to wait for the interactive sign-in")
    args = parser.parse_args(argv)
    root = args.root

    work = pending_work(root)
    if not (work["deposit"] or work["update"]):
        print("Nothing pending for BIROn; no session needed.")
        return 0
    _report_pending(work)

    if os.environ.get("BIRON_USERNAME") and os.environ.get("BIRON_PASSWORD"):
        print("BIROn uses BIRON_USERNAME/BIRON_PASSWORD; no browser session needed.")
        return 0

    cookie, source = _resolve_cookie(root)
    if cookie and _cookie_works(args.base_url, cookie):
        print("BIROn session on file still works.")
        return 0
    if cookie and source == "env":
        print(
            "the BIRON_COOKIE in .env is stale — replace it, or set "
            "BIRON_COOKIE=auto and run ./biron.sh login",
            file=sys.stderr,
        )
        return 1
    if os.environ.get("BIRON_NO_BROWSER"):
        print(
            "BIROn session missing or stale and no browser may be opened "
            "here (BIRON_NO_BROWSER) — run ./biron.sh session on the "
            "machine that starts the deploy",
            file=sys.stderr,
        )
        return 1

    print(f"BIROn session {'stale' if cookie else 'missing'}; "
          "refreshing silently through the browser profile…")
    try:
        cookie = cookiejar.harvest(root, headless=True)
    except cookiejar.LoginError as exc:
        print(f"silent refresh failed ({exc}); opening the sign-in window")
        try:
            cookie = cookiejar.harvest(
                root, headless=False, timeout=args.timeout
            )
        except cookiejar.LoginSkipped:
            print("continuing without a BIROn session; "
                  "the deposits retry on the next deploy")
            return EXIT_SKIPPED
        except cookiejar.LoginError as exc:
            print(f"BIROn sign-in failed: {exc}", file=sys.stderr)
            return 1
    if not _cookie_works(args.base_url, cookie):
        print(
            "the freshly harvested session was rejected by BIROn — run "
            "./biron.sh login and sign in interactively",
            file=sys.stderr,
        )
        return 1
    print("BIROn session ready.")
    return 0


def login_main(argv=None):
    parser = argparse.ArgumentParser(
        description="Log in to BIROn in a controlled browser and store the "
        "session cookie"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="silent refresh through the persisted Microsoft session "
        "(no window; fails when an interactive sign-in is required)",
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--timeout", type=float, default=None)
    args = parser.parse_args(argv)
    try:
        cookiejar.harvest(args.root, headless=args.headless, timeout=args.timeout)
    except cookiejar.LoginError as exc:
        sys.exit(str(exc))
    print("Done — verify with: ./biron.sh probe")
    return 0


def probe_main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check BIROn SWORD credentials and list deposit collections"
    )
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    client = _ensure_client(args.base_url, args.root)

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


def _describe(receipt: dict, status: str | None, base_url: str) -> str:
    """A human line for where the deposit landed, with a URL that works.

    The /id/eprint/NNN form only resolves once a record is public, so
    pending records get the workflow view URL instead.
    """
    eprintid = receipt["eprintid"]
    if status == "archive":
        return f"Deposited live: {base_url}/{eprintid}/"
    if status in ("inbox", "buffer"):
        return (
            f"Deposited to {status} (awaiting review): "
            f"{base_url}/cgi/users/home?screen=EPrint::View"
            f"&eprintid={eprintid}"
        )
    return f"Deposited: {receipt['url']}"


def _stamp_biron(repo_root: Path, post_path: Path, biron_url: str) -> None:
    """Write the biron: front-matter key using _biron's insertion logic."""
    spec = importlib.util.spec_from_file_location(
        "apply_biron", Path(repo_root) / "_biron" / "apply_biron.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    text = post_path.read_text(encoding="utf-8")
    post_path.write_text(
        module.insert_biron(text, biron=biron_url), encoding="utf-8"
    )


def finalise(client, post_path: Path, receipt: dict, base_url: str) -> str:
    """Stamp the post when its record went live; ledger it otherwise.

    Live records get the biron: key immediately (the link resolves right
    away); anything still in review goes into deposited.yml so it is not
    resent, and the _biron sweep stamps it once approved.
    """
    post_path = Path(post_path)
    repo_root = post_path.parent.parent
    status = client.eprint_status(receipt["eprintid"])
    if status == "archive":
        _stamp_biron(
            repo_root,
            post_path,
            f"{base_url}/id/eprint/{receipt['eprintid']}/",
        )
        record_shipped(
            repo_root / SHIPPED_PATH, post_path.name, file_digest(post_path)
        )
        return _describe(receipt, status, base_url) + " — biron: link stamped"
    record_deposit(
        repo_root / LEDGER_PATH, post_path.name, receipt["eprintid"]
    )
    return _describe(receipt, status, base_url)


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

    client = _ensure_client(args.base_url, args.post.parent.parent)
    collection = _resolve_collection(client, args)
    receipt = deposit_post(client, args.post, collection, pdf_path=args.pdf)
    print(finalise(client, args.post, receipt, args.base_url))
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

    client = _ensure_client(args.base_url, args.root)
    collection = _resolve_collection(client, args)
    for path in pending:
        try:
            receipt = deposit_post(client, path, collection)
        except FileNotFoundError as exc:
            print(f"SKIPPED {path.name}: {exc}", file=sys.stderr)
            continue
        except BironError as exc:
            sys.exit(f"FAILED {path.name}: {exc}")
        print(f"{path.name}: " + finalise(client, path, receipt, args.base_url))
    return 0
