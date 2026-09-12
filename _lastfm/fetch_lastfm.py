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
        error_path = root / ERROR_FILE
        error_path.parent.mkdir(parents=True, exist_ok=True)
        error_path.write_text(json.dumps(
            {"error": str(exc),
             "at": datetime.now(timezone.utc).isoformat(timespec="seconds")},
            ensure_ascii=False) + "\n")
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
    (root / ERROR_FILE).unlink(missing_ok=True)
    echo(f"fetch_lastfm: wrote {DATA_FILE} "
         f"({', '.join(k for k in ('last_played', 'top_track', 'top_artist', 'recent_plays') if k in store) or 'no stats'})")
    return 0


def main(argv=None):
    root = pathlib.Path(__file__).resolve().parent.parent
    return run(root, key=load_env_key(root))


if __name__ == "__main__":
    sys.exit(main())
