"""Back-importing Bluesky posts into the short-thoughts system.

Reads the account's app.bsky.feed.post records straight from its PDS
(public, no auth), converts top-level posts into thought entries —
replies are skipped, which also keeps thread continuations produced by
the composer itself out — and merges them into _data/thoughts.yml in
date order. Posts already syndicated from a thought are recognised by
their Bluesky URL and left alone, so the import is idempotent. Image
blobs are downloaded and stored through the same pipeline as composed
thoughts; URLs that Bluesky truncated for display are restored to their
full form from the link facets.
"""

from datetime import datetime, timedelta
from pathlib import Path

import requests

PUBLIC_APPVIEW = "https://public.api.bsky.app"
PLC_DIRECTORY = "https://plc.directory"
TIMEOUT = 30


class ImportError_(RuntimeError):
    """A Bluesky fetch the importer could not work around."""


def expand_links(text: str, facets: list | None) -> str:
    """Restore full URLs where Bluesky truncated the display text.

    Link facets carry the real URI with byte offsets into the UTF-8
    text; when the displayed span differs from the URI (…-shortened),
    the span is replaced so the thought carries a working link.
    """
    if not facets:
        return text
    raw = text.encode("utf-8")
    replacements = []
    for facet in facets:
        index = facet.get("index") or {}
        for feature in facet.get("features") or []:
            if feature.get("$type") == "app.bsky.richtext.facet#link":
                replacements.append(
                    (index.get("byteStart"), index.get("byteEnd"),
                     feature.get("uri", ""))
                )
    for start, end, uri in sorted(replacements, reverse=True):
        if start is None or end is None or not uri:
            continue
        if raw[start:end].decode("utf-8", "replace") != uri:
            raw = raw[:start] + uri.encode("utf-8") + raw[end:]
    return raw.decode("utf-8")


def existing_rkeys(thoughts: list[dict]) -> set[str]:
    """The Bluesky rkeys already present in the thoughts data."""
    return {
        thought["bluesky"].rstrip("/").rsplit("/", 1)[-1]
        for thought in thoughts
        if thought.get("bluesky")
    }


def _image_blobs(embed: dict | None) -> list[dict]:
    if not embed:
        return []
    if embed.get("$type") == "app.bsky.embed.recordWithMedia":
        return _image_blobs(embed.get("media"))
    if embed.get("$type") != "app.bsky.embed.images":
        return []
    blobs = []
    for image in embed.get("images") or []:
        blob = image.get("image") or {}
        cid = (blob.get("ref") or {}).get("$link")
        if cid:
            blobs.append(
                {
                    "cid": cid,
                    "mime": blob.get("mimeType", "image/jpeg"),
                    "alt": image.get("alt", ""),
                }
            )
    return blobs


def convert(record: dict, rkey: str, handle: str) -> dict | None:
    """A thought-shaped dict for one post record, or None to skip.

    Replies are skipped. The result carries the untouched (but
    link-expanded) text, the local-time date, the bsky.app URL, and an
    ``image_blobs`` list of ``{"cid", "mime", "alt"}`` still to be
    downloaded.
    """
    if record.get("reply"):
        return None
    created = datetime.fromisoformat(record["createdAt"]).astimezone()
    return {
        "date": created.isoformat(),
        "text": expand_links(record.get("text", ""), record.get("facets")),
        "bluesky": f"https://bsky.app/profile/{handle}/post/{rkey}",
        "image_blobs": _image_blobs(record.get("embed")),
    }


def assign_id(date: datetime, taken: set[str]) -> str:
    """A unique compact-timestamp id, bumping seconds on collision."""
    candidate = date
    while candidate.strftime("%Y%m%d%H%M%S") in taken:
        candidate += timedelta(seconds=1)
    new_id = candidate.strftime("%Y%m%d%H%M%S")
    taken.add(new_id)
    return new_id


def merge_thoughts(existing: list[dict], imported: list[dict]) -> list[dict]:
    """All entries newest-first; existing entries win their positions."""
    return sorted(
        list(existing) + list(imported),
        key=lambda thought: thought["date"],
        reverse=True,
    )


def _get(url, get=None, **kwargs):
    get = get or requests.get
    response = get(url, timeout=TIMEOUT, **kwargs)
    if response.status_code != 200:
        raise ImportError_(f"GET {url} -> HTTP {response.status_code}")
    return response


def resolve_pds(handle: str, get=None) -> tuple[str, str]:
    """(did, pds_base_url) for a handle, via the public AppView and PLC."""
    did = _get(
        f"{PUBLIC_APPVIEW}/xrpc/com.atproto.identity.resolveHandle",
        get=get,
        params={"handle": handle},
    ).json()["did"]
    document = _get(f"{PLC_DIRECTORY}/{did}", get=get).json()
    for service in document.get("service") or []:
        if service.get("type") == "AtprotoPersonalDataServer":
            return did, service["serviceEndpoint"].rstrip("/")
    raise ImportError_(f"no PDS endpoint in the DID document for {handle}")


def fetch_all_posts(pds: str, did: str, get=None) -> list[tuple[str, dict]]:
    """Every (rkey, record) in the repo's app.bsky.feed.post collection."""
    posts = []
    cursor = None
    while True:
        params = {
            "repo": did,
            "collection": "app.bsky.feed.post",
            "limit": 100,
        }
        if cursor:
            params["cursor"] = cursor
        page = _get(
            f"{pds}/xrpc/com.atproto.repo.listRecords", get=get, params=params
        ).json()
        for item in page.get("records") or []:
            posts.append((item["uri"].rsplit("/", 1)[-1], item["value"]))
        cursor = page.get("cursor")
        if not cursor:
            return posts


def fetch_blob(pds: str, did: str, cid: str, get=None) -> bytes:
    """One image blob's bytes."""
    return _get(
        f"{pds}/xrpc/com.atproto.sync.getBlob",
        get=get,
        params={"did": did, "cid": cid},
    ).content


def main(argv=None):
    import argparse

    from .store import DATA_PATH, load_thoughts, save_image
    from .store import _write as write_thoughts

    parser = argparse.ArgumentParser(
        description="Back-import Bluesky posts into the short-thoughts data"
    )
    parser.add_argument("--handle", default="eve.gd")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    existing = load_thoughts(args.root)
    known = existing_rkeys(existing)
    did, pds = resolve_pds(args.handle)
    print(f"{args.handle} -> {did} on {pds}")

    posts = fetch_all_posts(pds, did)
    print(f"records fetched: {len(posts)}")

    candidates = []
    skipped_replies = skipped_known = 0
    for rkey, record in posts:
        if rkey in known:
            skipped_known += 1
            continue
        thought = convert(record, rkey, args.handle)
        if thought is None:
            skipped_replies += 1
            continue
        candidates.append(thought)
    candidates.sort(key=lambda thought: thought["date"])
    print(
        f"to import: {len(candidates)} "
        f"(skipped {skipped_replies} replies, "
        f"{skipped_known} already-syndicated)"
    )
    if args.dry_run:
        for thought in candidates:
            images = len(thought["image_blobs"])
            note = f" [{images} image(s)]" if images else ""
            print(f"  {thought['date'][:16]}{note} {thought['text'][:60]!r}")
        return 0
    if not candidates:
        print("Nothing to import.")
        return 0

    backup = args.root / f".thoughts-backup-{datetime.now().astimezone():%Y%m%d%H%M%S}.yml"
    data_file = args.root / DATA_PATH
    if data_file.exists():
        backup.write_bytes(data_file.read_bytes())
        print(f"backup written: {backup}")

    taken = {thought["id"] for thought in existing}
    imported = []
    for thought in candidates:
        thought_id = assign_id(
            datetime.fromisoformat(thought["date"]), taken
        )
        entry = {
            "id": thought_id,
            "date": thought["date"],
            "text": thought["text"],
        }
        images = []
        for seq, blob in enumerate(thought.pop("image_blobs"), 1):
            data = fetch_blob(pds, did, blob["cid"])
            image_entry, _, _ = save_image(
                args.root, data, blob["mime"], thought_id, seq,
                alt=blob["alt"],
            )
            images.append(image_entry)
        if images:
            entry["images"] = images
        entry["bluesky"] = thought["bluesky"]
        imported.append(entry)
        print(f"imported {entry['date'][:16]} {entry['text'][:60]!r}")

    write_thoughts(args.root, merge_thoughts(existing, imported))
    print(f"done: {len(imported)} thought(s) added to {data_file}")
    return 0
