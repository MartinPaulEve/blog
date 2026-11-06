#!/usr/bin/env python3
"""Pull Last.fm listening stats into _data/lastfm.json.

Run from the blog root (stdlib only, no third-party deps):

    uv run _lastfm/fetch_lastfm.py

Reads the API key from $LASTFM_API_KEY (falling back to the .env file at
the blog root). Without a key the script is a friendly no-op so deploys
keep working before the API account exists (create a key at
https://www.last.fm/api/account/create).

The data file is a small snapshot the sidebar widget renders at build time:

    {"updated": "...", "user": "MartinPaulEve",
     "url": "https://www.last.fm/user/MartinPaulEve",
     "last_played": {"track": ..., "artist": ..., "artist_url": ...,
                     "url": ..., "now_playing": false},
     "recent_plays": [{"track": ..., "artist": ..., "artist_url": ...,
                       "url": ...}, ...],
     "top_track": {"track": ..., "artist": ..., "artist_url": ...,
                   "url": ..., "playcount": 1},
     "top_artist": {"artist": ..., "url": ..., "playcount": 1}}

The recent plays are a random sample of the last RECENT_LIMIT scrobbles,
at most one track per artist, re-drawn on every fetch.

The same run keeps _data/listening.json, the full play log behind the
/listening/ pages, up to date (see the listening-log section below).

No artwork is fetched or hotlinked: the widget is text-only, so serving the
site keeps adding no third-party requests.
"""

from __future__ import annotations

import json
import os
import pathlib
import random
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API_URL = "https://ws.audioscrobbler.com/2.0/"
USER = "MartinPaulEve"
PROFILE_URL = f"https://www.last.fm/user/{USER}"
DATA_FILE = "_data/lastfm.json"
ERROR_FILE = "_lastfm/fetch_error.json"
TIMEOUT = 30
RECENT_LIMIT = 50
RECENT_SAMPLE = 5


def load_env_key(root):
    """LASTFM_API_KEY from the environment or the root .env file."""
    key = os.environ.get("LASTFM_API_KEY")
    if key:
        return key
    env_file = pathlib.Path(root) / ".env"
    if env_file.is_file():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("LASTFM_API_KEY="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                return value or None
    return None


def api_url(method, key, **params):
    """The JSON API URL for one method call against USER."""
    query = {"method": method, "user": USER, "api_key": key,
             "format": "json", **params}
    return API_URL + "?" + urllib.parse.urlencode(query)


_SSL_CONTEXT = None


def _ssl_context():
    """Default TLS context, falling back to the system CA bundle: the
    uv-managed Python on NixOS ships with an empty default cert store."""
    global _SSL_CONTEXT
    if _SSL_CONTEXT is None:
        _SSL_CONTEXT = ssl.create_default_context()
        if not _SSL_CONTEXT.get_ca_certs():
            for bundle in ("/etc/ssl/certs/ca-certificates.crt",
                           "/etc/ssl/certs/ca-bundle.crt"):
                if pathlib.Path(bundle).is_file():
                    _SSL_CONTEXT.load_verify_locations(bundle)
                    break
    return _SSL_CONTEXT


def http_get_json(url):
    """GET a URL and decode the JSON body."""
    request = urllib.request.Request(url, headers={"User-Agent": "eve.gd"})
    with urllib.request.urlopen(request, timeout=TIMEOUT,
                                context=_ssl_context()) as response:
        return json.loads(response.read().decode("utf-8"))


def _tracks(payload, section, kind):
    entries = payload.get(section, {}).get(kind, []) if isinstance(
        payload, dict) else []
    if isinstance(entries, dict):
        entries = [entries]
    return entries


def _artist_name(artist):
    if isinstance(artist, dict):
        return artist.get("name") or artist.get("#text") or ""
    return str(artist or "")


def _artist_url(artist):
    """The artist's Last.fm page, built from the name when the payload
    carries none (plain user.getrecenttracks artists are just a #text)."""
    if isinstance(artist, dict) and artist.get("url"):
        return artist["url"]
    name = _artist_name(artist)
    if not name:
        return ""
    return "https://www.last.fm/music/" + urllib.parse.quote_plus(name)


def parse_last_played(payload):
    """The most recent scrobble from a user.getrecenttracks payload."""
    entries = _tracks(payload, "recenttracks", "track")
    if not entries:
        return None
    first = entries[0]
    playing = first.get("@attr", {}).get("nowplaying") == "true"
    return {"track": first.get("name", ""),
            "artist": _artist_name(first.get("artist")),
            "artist_url": _artist_url(first.get("artist")),
            "url": first.get("url", ""),
            "now_playing": playing}


def parse_recent_plays(payload, count=RECENT_SAMPLE, exclude=None, rng=random):
    """A random sample of recent scrobbles, at most one track per artist.

    Now-playing entries and the `exclude` track (the one already shown as
    "last played") are left out; the same artist with a different track
    stays eligible.
    """
    excluded = None
    if exclude:
        excluded = (exclude.get("track", "").casefold(),
                    exclude.get("artist", "").casefold())
    pool, seen_tracks = [], set()
    for entry in _tracks(payload, "recenttracks", "track"):
        if entry.get("@attr", {}).get("nowplaying") == "true":
            continue
        name = entry.get("name", "")
        artist = _artist_name(entry.get("artist"))
        if not name or not artist:
            continue
        key = (name.casefold(), artist.casefold())
        if key == excluded or key in seen_tracks:
            continue
        seen_tracks.add(key)
        pool.append({"track": name, "artist": artist,
                     "artist_url": _artist_url(entry.get("artist")),
                     "url": entry.get("url", "")})
    rng.shuffle(pool)
    plays, seen_artists = [], set()
    for play in pool:
        artist_key = play["artist"].casefold()
        if artist_key in seen_artists:
            continue
        seen_artists.add(artist_key)
        plays.append(play)
        if len(plays) >= count:
            break
    return plays


def parse_top_track(payload):
    """The all-time most played track from a user.gettoptracks payload."""
    entries = _tracks(payload, "toptracks", "track")
    if not entries:
        return None
    first = entries[0]
    return {"track": first.get("name", ""),
            "artist": _artist_name(first.get("artist")),
            "artist_url": _artist_url(first.get("artist")),
            "url": first.get("url", ""),
            "playcount": int(first.get("playcount", 0))}


def parse_top_artist(payload):
    """The all-time most played artist from a user.gettopartists payload."""
    entries = _tracks(payload, "topartists", "artist")
    if not entries:
        return None
    first = entries[0]
    return {"artist": first.get("name", ""),
            "url": first.get("url", ""),
            "playcount": int(first.get("playcount", 0))}


def build_store(last_played, top_track, top_artist, recent_plays, now):
    """The _data/lastfm.json document; sections that are empty are omitted."""
    store = {"updated": now, "user": USER, "url": PROFILE_URL}
    if last_played:
        store["last_played"] = last_played
    if top_track:
        store["top_track"] = top_track
    if top_artist:
        store["top_artist"] = top_artist
    if recent_plays:
        store["recent_plays"] = recent_plays
    return store


def run(root, key=None, get=http_get_json, echo=print, rng=random):
    """Fetch all three stats and write the data file; returns an exit code.

    All-or-nothing: any endpoint failing leaves the existing data file in
    place, so a flaky API can only ever serve stale stats, never partial
    ones.
    """
    root = pathlib.Path(root)
    if not key:
        echo("fetch_lastfm: no LASTFM_API_KEY set; skipping (create a key "
             "at https://www.last.fm/api/account/create and add it to .env)")
        return 0

    try:
        # extended=1 makes each artist a full object carrying its page URL.
        recent = get(api_url("user.getrecenttracks", key,
                             limit=RECENT_LIMIT, extended=1))
        top_tracks = get(api_url("user.gettoptracks", key,
                                 period="overall", limit=1))
        top_artists = get(api_url("user.gettopartists", key,
                                  period="overall", limit=1))
    except (RuntimeError, OSError, ValueError) as exc:
        echo(f"fetch_lastfm: fetch failed: {exc}")
        # Leave a sentinel for _plugins/lastfm_check.rb, which reports the
        # failure in every build's output until a fetch succeeds again.
        _write_error(root, str(exc))
        return 1

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    last_played = parse_last_played(recent)
    store = build_store(last_played,
                        parse_top_track(top_tracks),
                        parse_top_artist(top_artists),
                        parse_recent_plays(recent, exclude=last_played,
                                           rng=rng), now)
    data_path = root / DATA_FILE
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(
        json.dumps(store, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    echo(f"fetch_lastfm: wrote {DATA_FILE} "
         f"({', '.join(k for k in ('last_played', 'top_track', 'top_artist', 'recent_plays') if k in store) or 'no stats'})")

    if not sync_listening(root, key, get=get, echo=echo):
        _write_error(root, "listening log sync failed")
        return 1
    (root / ERROR_FILE).unlink(missing_ok=True)
    return 0


def _write_error(root, message):
    """Leave the sentinel _plugins/lastfm_check.rb reports on every build."""
    error_path = pathlib.Path(root) / ERROR_FILE
    error_path.parent.mkdir(parents=True, exist_ok=True)
    error_path.write_text(json.dumps(
        {"error": message,
         "at": datetime.now(timezone.utc).isoformat(timespec="seconds")},
        ensure_ascii=False) + "\n")


# --- the full listening log (_data/listening.json) -------------------------
#
# Every scrobble, newest first, for the /listening/ pages:
#
#     {"updated": "...", "user": ..., "url": ..., "through": <unix ts>,
#      "plays": [{"ts": <unix ts>, "date": "<ISO, local zone>",
#                 "track": ..., "artist": ..., "artist_url": ..., "url": ...,
#                 "album": ...(when known), "n": <plays>(when > 1)}, ...]}
#
# A track played several times in a row is one entry carrying "n", the
# count, under the timestamp of its first play. "through" is the newest
# scrobble ever folded in: the next sync asks Last.fm only for plays
# after it, so a run can keep growing across deploys. Dates are local
# (TZ, Europe/London in the deploy container) so the month pages split
# where the calendar does.

LISTENING_FILE = "_data/listening.json"
PAGE_LIMIT = 200


def _play_key(play):
    return (play.get("track", "").casefold(), play.get("artist", "").casefold())


def parse_scrobbles(payload, tz=None):
    """Every dated play in a user.getrecenttracks page, in payload order.

    The now-playing entry has no timestamp and is skipped; ``tz`` is the
    zone the ISO date is written in (None: the local zone).
    """
    plays = []
    for entry in _tracks(payload, "recenttracks", "track"):
        if entry.get("@attr", {}).get("nowplaying") == "true":
            continue
        try:
            ts = int((entry.get("date") or {}).get("uts", ""))
        except (TypeError, ValueError):
            continue
        name = entry.get("name", "")
        artist = _artist_name(entry.get("artist"))
        if not name or not artist:
            continue
        when = datetime.fromtimestamp(ts, timezone.utc).astimezone(tz)
        play = {"ts": ts,
                "date": when.isoformat(timespec="seconds"),
                "track": name,
                "artist": artist,
                "artist_url": _artist_url(entry.get("artist")),
                "url": entry.get("url", "")}
        album = entry.get("album")
        album = album.get("#text", "") if isinstance(album, dict) else str(album or "")
        if album:
            play["album"] = album
        plays.append(play)
    return plays


def merge_plays(plays, fresh, through=0):
    """Fold fresh plays into the newest-first log; returns (plays, through).

    Only plays after ``through`` count, each timestamp once. Taken oldest
    first, a play of the same track (case-insensitively, same artist) as
    the log's newest entry extends that entry's run (``n``) instead of
    adding a line; anything else goes on the front.
    """
    plays = [dict(play) for play in plays]
    seen = set()
    for play in sorted(fresh, key=lambda play: play["ts"]):
        ts = play["ts"]
        if ts <= through or ts in seen:
            continue
        seen.add(ts)
        if plays and _play_key(plays[0]) == _play_key(play):
            plays[0]["n"] = plays[0].get("n", 1) + 1
        else:
            plays.insert(0, {k: v for k, v in play.items() if k != "n"})
        through = ts
    return plays, through


def fetch_scrobbles(key, get=http_get_json, since=0):
    """Every raw recent-tracks entry after ``since``, across all pages.

    Pages run newest first; ``since`` is Last.fm's exclusive ``from``.
    A page without paging attributes is taken to be the only one.
    """
    params = {"limit": PAGE_LIMIT, "extended": 1}
    if since:
        params["from"] = since
    entries = []
    page, total_pages = 1, 1
    while page <= total_pages:
        payload = get(api_url("user.getrecenttracks", key, page=page, **params))
        entries.extend(_tracks(payload, "recenttracks", "track"))
        attr = payload.get("recenttracks", {}).get("@attr", {}) if isinstance(
            payload, dict) else {}
        try:
            total_pages = int(attr.get("totalPages", 1))
        except (TypeError, ValueError):
            total_pages = 1
        page += 1
    return entries


def load_listening(root):
    """The stored log, or an empty one when the file is absent.

    A corrupt file raises (ValueError) rather than reading as empty: an
    empty log would be refilled from scratch and silently overwrite it.
    """
    path = pathlib.Path(root) / LISTENING_FILE
    if not path.is_file():
        return {"plays": [], "through": 0}
    log = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(log, dict):
        raise ValueError(f"{LISTENING_FILE} is not a JSON object")
    log.setdefault("plays", [])
    log.setdefault("through", 0)
    return log


def sync_listening(root, key, get=http_get_json, echo=print, tz=None,
                   now=None):
    """Bring the listening log up to date; True unless the fetch failed.

    Fetches only what Last.fm has after the log's ``through`` and folds
    it in. Nothing new leaves the file untouched (so a deploy with no
    listening in between commits nothing here); a failed fetch or an
    unreadable log leaves the file alone and reports.
    """
    root = pathlib.Path(root)
    try:
        log = load_listening(root)
        fresh = parse_scrobbles(
            {"recenttracks": {"track": fetch_scrobbles(
                key, get=get, since=log["through"])}}, tz=tz)
    except (RuntimeError, OSError, ValueError) as exc:
        echo(f"fetch_lastfm: listening log sync failed: {exc}")
        return False
    plays, through = merge_plays(log["plays"], fresh, log["through"])
    if through == log["through"] and plays == log["plays"]:
        echo(f"fetch_lastfm: {LISTENING_FILE} already current "
             f"({len(plays)} entries)")
        return True
    log.update({
        "updated": now or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "user": USER,
        "url": PROFILE_URL,
        "through": through,
        "plays": plays,
    })
    path = root / LISTENING_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(log, indent=1, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    echo(f"fetch_lastfm: wrote {LISTENING_FILE} "
         f"(+{len(fresh)} play(s), {len(plays)} entries)")
    return True


def main(argv=None):
    root = pathlib.Path(__file__).resolve().parent.parent
    return run(root, key=load_env_key(root))


if __name__ == "__main__":
    sys.exit(main())
