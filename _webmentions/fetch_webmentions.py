#!/usr/bin/env python3
"""Pull this site's webmentions from webmention.io into _data/webmentions.json.

Run from the blog root (stdlib only, no third-party deps):

    uv run _webmentions/fetch_webmentions.py [--full]

Reads the API token from $WEBMENTION_IO_TOKEN (falling back to the .env file
at the blog root). Without a token the script is a friendly no-op so deploys
keep working before the webmention.io account exists.

The data file groups mentions per target path and per kind so the Liquid
templates stay trivial:

    {"updated": "...", "last_wm_id": 123,
     "targets": {"/2026/01/01/a-post/": {"likes": [...], "reposts": [...],
                 "replies": [...], "mentions": [...], "bookmarks": [...]}}}

Author avatars are copied into images/webmentions/ at fetch time so serving
the site never hotlinks a third-party image (the site is otherwise free of
third-party requests and stays that way).
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API_URL = "https://webmention.io/api/mentions.jf2"
SITE_HOSTS = {"eve.gd", "www.eve.gd"}
DATA_FILE = "_data/webmentions.json"
AVATAR_DIR = "images/webmentions"
PER_PAGE = 100
KINDS = ("likes", "reposts", "replies", "mentions", "bookmarks")
MAX_TEXT = 1500
TIMEOUT = 30

EMPTY_STORE = {"updated": None, "last_wm_id": 0, "targets": {}}

KIND_BY_PROPERTY = {
    "like-of": "likes",
    "repost-of": "reposts",
    "in-reply-to": "replies",
    "mention-of": "mentions",
    "bookmark-of": "bookmarks",
}

# Raster formats only: an SVG avatar could carry scripts and would be served
# from this domain, so anything else is silently dropped.
EXT_BY_TYPE = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/avif": ".avif",
}


def http_get(url):
    """GET a URL; returns (status, headers dict, body bytes)."""
    request = urllib.request.Request(
        url, headers={"User-Agent": "eve.gd-webmentions/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers or {}), b""


def target_path(url):
    """Canonical site-relative path for a mention target, or None.

    Accepts http/https and the www host, strips query/fragment, adds the
    trailing slash our permalinks carry, and percent-encodes non-ASCII the
    way Jekyll writes doc.url — so the result always matches page.url.
    """
    parts = urllib.parse.urlsplit(url or "")
    if parts.scheme not in ("http", "https") or parts.hostname not in SITE_HOSTS:
        return None
    path = urllib.parse.quote(urllib.parse.unquote(parts.path or "/"), safe="/")
    if not path.endswith("/"):
        path += "/"
    return path


def classify(entry):
    """Map a jf2 entry's wm-property onto one of KINDS."""
    return KIND_BY_PROPERTY.get(entry.get("wm-property"), "mentions")


def simplify(entry, avatar):
    """Reduce a jf2 entry to the fields the templates render.

    ``avatar`` is a callable mapping a photo URL to a local path (or None).
    """
    author = entry.get("author") or {}
    content = entry.get("content") or {}
    photo = author.get("photo") or ""
    return {
        "wm_id": entry.get("wm-id"),
        "url": entry.get("url") or entry.get("wm-source") or "",
        "author_name": author.get("name") or "",
        "author_url": author.get("url") or "",
        "avatar": avatar(photo) if photo else None,
        "published": entry.get("published") or entry.get("wm-received") or "",
        "text": (content.get("text") or "")[:MAX_TEXT],
    }


def merge(store, entries, avatar):
    """Fold raw jf2 entries into a store dict; returns the new store.

    Groups by target path and kind, replaces duplicates by wm-id (a re-sent
    mention may even have changed kind), drops targets outside the site,
    keeps every kind sorted by published date, and advances last_wm_id.
    """
    store = copy.deepcopy(store)
    targets = store.setdefault("targets", {})
    last_wm_id = store.get("last_wm_id") or 0

    for raw in entries:
        path = target_path(raw.get("wm-target"))
        if path is None:
            continue
        bucket = targets.setdefault(path, {kind: [] for kind in KINDS})
        simple = simplify(raw, avatar)
        for kind in KINDS:
            bucket[kind] = [e for e in bucket[kind] if e["wm_id"] != simple["wm_id"]]
        bucket[classify(raw)].append(simple)
        if isinstance(simple["wm_id"], int):
            last_wm_id = max(last_wm_id, simple["wm_id"])

    for bucket in targets.values():
        for kind in KINDS:
            bucket[kind].sort(key=lambda e: (e.get("published") or "",
                                             e.get("wm_id") or 0))
    store["last_wm_id"] = last_wm_id
    return store


def fetch_all(get, token, since_id=0):
    """Page through the webmention.io API; returns the raw jf2 entries."""
    entries, page = [], 0
    while True:
        params = {"token": token, "per-page": PER_PAGE, "page": page}
        if since_id:
            params["since_id"] = since_id
        status, _headers, body = get(f"{API_URL}?{urllib.parse.urlencode(params)}")
        if status != 200:
            raise RuntimeError(f"webmention.io API returned {status}")
        children = json.loads(body.decode("utf-8")).get("children") or []
        entries.extend(children)
        if len(children) < PER_PAGE:
            return entries
        page += 1


def cache_avatar(url, dest_dir, get):
    """Download an author photo into dest_dir; returns the site path or None."""
    if not url:
        return None
    dest_dir = pathlib.Path(dest_dir)
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    existing = sorted(dest_dir.glob(f"{digest}.*"))
    if existing:
        return f"/{AVATAR_DIR}/{existing[0].name}"
    try:
        status, headers, body = get(url)
    except OSError:
        return None
    if status != 200 or not body:
        return None
    content_type = {k.lower(): v for k, v in headers.items()}.get("content-type", "")
    extension = EXT_BY_TYPE.get(content_type.split(";")[0].strip().lower())
    if extension is None:
        return None
    filename = digest + extension
    (dest_dir / filename).write_bytes(body)
    return f"/{AVATAR_DIR}/{filename}"


def load_env_token(root):
    """WEBMENTION_IO_TOKEN from the environment or the root .env file."""
    token = os.environ.get("WEBMENTION_IO_TOKEN")
    if token:
        return token
    env_file = pathlib.Path(root) / ".env"
    if env_file.is_file():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("WEBMENTION_IO_TOKEN="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                return value or None
    return None


def run(root, get=http_get, token=None, full=False, echo=print):
    """Fetch, merge and write; returns a process exit code."""
    root = pathlib.Path(root)
    if not token:
        echo("fetch_webmentions: no WEBMENTION_IO_TOKEN set; skipping "
             "(sign up at https://webmention.io and add the token to .env)")
        return 0

    data_path = root / DATA_FILE
    store = copy.deepcopy(EMPTY_STORE)
    if data_path.is_file():
        store = json.loads(data_path.read_text())

    since_id = 0 if full else store.get("last_wm_id") or 0
    try:
        entries = fetch_all(get, token, since_id=since_id)
    except (RuntimeError, OSError, ValueError) as exc:
        echo(f"fetch_webmentions: fetch failed: {exc}")
        return 1

    avatar_dir = root / AVATAR_DIR
    avatar_dir.mkdir(parents=True, exist_ok=True)

    def avatar(url):
        return cache_avatar(url, avatar_dir, get)

    base = copy.deepcopy(EMPTY_STORE) if full else store
    merged = merge(base, entries, avatar)
    merged["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(
        json.dumps(merged, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    echo(f"fetch_webmentions: merged {len(entries)} mention(s); "
         f"store covers {len(merged['targets'])} target(s)")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true",
                        help="refetch everything and rebuild the data file")
    args = parser.parse_args(argv)
    root = pathlib.Path(__file__).resolve().parent.parent
    return run(root, token=load_env_token(root), full=args.full)


if __name__ == "__main__":
    sys.exit(main())
