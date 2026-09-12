"""Back-importing an official X/Twitter archive into short thoughts.

Works from the self-service archive ZIP (Settings → Download an archive
of your data) or its extracted folder: ``data/tweets*.js`` holds every
tweet with untruncated text and URL entities, ``data/tweets_media/``
holds the original image files. The same editorial rules as the Bluesky
importer apply: retweets and replies to other people are dropped
(including old-style tweets that open with an @mention), replies solely
to the author's own tweets are appended to their root tweet as a
thread, and posts that are just a link to eve.gd / martineve.com are
pruned — after t.co links have been expanded back to their real URLs,
so blog-announcement tweets are recognised. Entries link back to the
original at twitter.com and render as "Twitter" on /thoughts/.
"""

import json
import re
import zipfile
from datetime import datetime
from pathlib import Path

from .importer import is_announcement

CREATED_AT_FORMAT = "%a %b %d %H:%M:%S %z %Y"
MIME_BY_EXTENSION = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


class ArchiveError(RuntimeError):
    """An archive that cannot be read or parsed."""


def strip_js_preamble(text: str) -> list:
    """The JSON payload of a window.YTD.*.partN = [...] archive file."""
    position = text.find("=")
    if position == -1:
        raise ArchiveError("archive file carries no assignment preamble")
    return json.loads(text[position + 1:])


def expand_tco(full_text: str, entities: dict | None) -> str:
    """Restore t.co wrappers to their real URLs; drop media t.co stubs.

    ``entities.urls`` carry expanded_url for links the author wrote;
    ``entities.media`` t.co stubs point at the attached image, which is
    imported as a file, so the stub is removed from the text.
    """
    if not entities:
        return full_text
    text = full_text
    for url in entities.get("urls") or []:
        if url.get("url") and url.get("expanded_url"):
            text = text.replace(url["url"], url["expanded_url"])
    for media in entities.get("media") or []:
        if media.get("url"):
            text = text.replace(media["url"], "")
    return re.sub(r"[ \t]+", " ", text).strip()


def parse_created_at(created_at: str) -> datetime:
    """The tweet's timestamp, converted to the local timezone."""
    return datetime.strptime(created_at, CREATED_AT_FORMAT).astimezone()


def media_files(tweet: dict) -> list[dict]:
    """The photo attachments as {"name", "mime", "alt"} archive entries.

    Names follow the archive convention <tweet_id>-<media basename>.
    Videos and animated GIFs are skipped (only a thumbnail exists).
    """
    media_entities = (
        (tweet.get("extended_entities") or tweet.get("entities") or {})
        .get("media") or []
    )
    files = []
    for media in media_entities:
        if media.get("type", "photo") != "photo":
            continue
        source = media.get("media_url_https") or media.get("media_url") or ""
        basename = source.rsplit("/", 1)[-1]
        extension = "." + basename.rsplit(".", 1)[-1].lower() if "." in basename else ""
        if not basename or extension not in MIME_BY_EXTENSION:
            continue
        files.append(
            {
                "name": f"{tweet['id_str']}-{basename}",
                "mime": MIME_BY_EXTENSION[extension],
                "alt": media.get("ext_alt_text") or "",
            }
        )
    return files


def existing_tweet_ids(thoughts: list[dict]) -> set[str]:
    """The tweet status ids already present in the thoughts data."""
    return {
        thought["twitter"].rstrip("/").rsplit("/", 1)[-1]
        for thought in thoughts
        if thought.get("twitter")
    }


def _tweet_thought(tweet: dict, handle: str) -> dict:
    return {
        "date": parse_created_at(tweet["created_at"]).isoformat(),
        "text": expand_tco(tweet.get("full_text", ""), tweet.get("entities")),
        "twitter": f"https://twitter.com/{handle}/status/{tweet['id_str']}",
        "image_files": media_files(tweet),
    }


def build_tweet_thoughts(
    tweets: list[dict],
    handle: str,
    own_user_id: str,
    known: set[str],
):
    """(thoughts, stats) from unwrapped tweet dicts.

    Top-level tweets become thoughts; retweets, @-opening tweets and
    replies to others are dropped; self-reply chains are appended to
    their root tweet (text and media, chronologically); announcement
    tweets (just a link to the blog) are pruned along with their
    threads.
    """
    stats = {
        "known": 0, "retweets": 0, "replies": 0,
        "announcements": 0, "threaded": 0,
    }
    by_id = {tweet["id_str"]: tweet for tweet in tweets}
    roots: dict[str, dict] = {}
    pending_replies = []

    for tweet in tweets:
        if tweet["id_str"] in known:
            stats["known"] += 1
            continue
        text = tweet.get("full_text", "")
        if text.startswith("RT @"):
            stats["retweets"] += 1
            continue
        if tweet.get("in_reply_to_status_id_str"):
            pending_replies.append(tweet)
            continue
        if text.startswith("@"):
            stats["replies"] += 1
            continue
        thought = _tweet_thought(tweet, handle)
        if is_announcement(thought["text"]):
            stats["announcements"] += 1
            continue
        roots[tweet["id_str"]] = thought

    def resolve_root(tweet: dict, seen: set[str]) -> str | None:
        """The candidate root of a pure self-reply chain, or None."""
        if tweet.get("in_reply_to_user_id_str") != own_user_id:
            return None
        parent_id = tweet.get("in_reply_to_status_id_str")
        if parent_id in seen:
            return None
        if parent_id in roots:
            return parent_id
        parent = by_id.get(parent_id)
        if parent is None or not parent.get("in_reply_to_status_id_str"):
            return None
        return resolve_root(parent, seen | {parent_id})

    continuations: dict[str, list[dict]] = {}
    for tweet in pending_replies:
        root_id = resolve_root(tweet, {tweet["id_str"]})
        if root_id is None:
            stats["replies"] += 1
            continue
        continuations.setdefault(root_id, []).append(
            _tweet_thought(tweet, handle)
        )
        stats["threaded"] += 1

    for root_id, chain in continuations.items():
        target = roots[root_id]
        for continuation in sorted(chain, key=lambda c: c["date"]):
            target["text"] += "\n\n" + continuation["text"]
            target["image_files"] += continuation["image_files"]

    thoughts = sorted(roots.values(), key=lambda thought: thought["date"])
    return thoughts, stats


class Archive:
    """Uniform reader over the archive ZIP or its extracted folder."""

    def __init__(self, path: Path):
        self.path = Path(path)
        if not self.path.exists():
            raise ArchiveError(f"{self.path} does not exist")
        self._zip = (
            zipfile.ZipFile(self.path) if self.path.is_file() else None
        )

    def read_bytes(self, name: str) -> bytes:
        if self._zip:
            return self._zip.read(name)
        return (self.path / name).read_bytes()

    def read_text(self, name: str) -> str:
        return self.read_bytes(name).decode("utf-8")

    def names(self) -> list[str]:
        if self._zip:
            return self._zip.namelist()
        return [
            str(entry.relative_to(self.path))
            for entry in self.path.rglob("*")
            if entry.is_file()
        ]

    def has(self, name: str) -> bool:
        if self._zip:
            return name in self._zip.namelist()
        return (self.path / name).is_file()

    def account(self) -> tuple[str, str]:
        """(username, account_id) from data/account.js."""
        try:
            payload = strip_js_preamble(self.read_text("data/account.js"))
            account = payload[0]["account"]
            return account["username"], account["accountId"]
        except (KeyError, IndexError, OSError) as exc:
            raise ArchiveError(f"cannot read data/account.js: {exc}") from exc

    def tweets(self) -> list[dict]:
        """Every tweet, unwrapped, from all data/tweets*.js parts."""
        parts = sorted(
            name for name in self.names()
            if re.fullmatch(r"data/tweets(-part\d+)?\.js", name)
        )
        if not parts:
            raise ArchiveError("no data/tweets*.js files in the archive")
        tweets = []
        for part in parts:
            for wrapper in strip_js_preamble(self.read_text(part)):
                tweets.append(wrapper.get("tweet", wrapper))
        return tweets


def main(argv=None):
    import argparse

    from .importer import assign_id, merge_thoughts
    from .store import DATA_PATH, load_thoughts, save_image
    from .store import _write as write_thoughts

    parser = argparse.ArgumentParser(
        description="Back-import an X/Twitter archive into short thoughts"
    )
    parser.add_argument(
        "archive", type=Path,
        help="the archive ZIP or its extracted folder",
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--handle", default=None,
        help="override the handle used in twitter.com links "
        "(default: the archive's own username)",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    archive = Archive(args.archive)
    username, account_id = archive.account()
    handle = args.handle or username
    print(f"archive account: @{username} ({account_id})")

    tweets = archive.tweets()
    print(f"tweets in archive: {len(tweets)}")

    existing = load_thoughts(args.root)
    known = existing_tweet_ids(existing)
    candidates, stats = build_tweet_thoughts(
        tweets, handle, account_id, known
    )
    print(
        f"to import: {len(candidates)} "
        f"(threaded {stats['threaded']} self-replies into their roots; "
        f"skipped {stats['retweets']} retweets, {stats['replies']} replies, "
        f"{stats['announcements']} blog-announcement posts, "
        f"{stats['known']} already imported)"
    )
    if args.dry_run:
        for thought in candidates:
            images = len(thought["image_files"])
            note = f" [{images} image(s)]" if images else ""
            print(f"  {thought['date'][:16]}{note} {thought['text'][:60]!r}")
        return 0
    if not candidates:
        print("Nothing to import.")
        return 0

    backup = (
        args.root
        / f".thoughts-backup-{datetime.now().astimezone():%Y%m%d%H%M%S}.yml"
    )
    data_file = args.root / DATA_PATH
    if data_file.exists():
        backup.write_bytes(data_file.read_bytes())
        print(f"backup written: {backup}")

    taken = {thought["id"] for thought in existing}
    imported = []
    missing_media = 0
    for thought in candidates:
        thought_id = assign_id(datetime.fromisoformat(thought["date"]), taken)
        entry = {
            "id": thought_id,
            "date": thought["date"],
            "text": thought["text"],
        }
        images = []
        for seq, spec in enumerate(thought.pop("image_files"), 1):
            name = f"data/tweets_media/{spec['name']}"
            if not archive.has(name):
                missing_media += 1
                continue
            image_entry, _, _ = save_image(
                args.root, archive.read_bytes(name), spec["mime"],
                thought_id, seq, alt=spec["alt"],
            )
            images.append(image_entry)
        if images:
            entry["images"] = images
        entry["twitter"] = thought["twitter"]
        imported.append(entry)

    write_thoughts(args.root, merge_thoughts(existing, imported))
    print(f"done: {len(imported)} thought(s) added to {data_file}")
    if missing_media:
        print(f"note: {missing_media} media file(s) absent from the archive")
    return 0
