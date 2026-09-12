"""Behavioural tests for the Last.fm fetch script (run from the blog root):

    uv run --with pytest -m pytest _tests/test_fetch_lastfm.py
"""

import json
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_lastfm"))

import fetch_lastfm as lf


def recent_payload(now_playing=False, empty=False, single_dict=False):
    if empty:
        return {"recenttracks": {"track": []}}
    track = {
        "artist": {"mbid": "", "#text": "Fluke"},
        "name": "Atom Bomb",
        "url": "https://www.last.fm/music/Fluke/_/Atom+Bomb",
        "date": {"uts": "1757200000", "#text": "07 Sep 2026, 10:00"},
    }
    if now_playing:
        track["@attr"] = {"nowplaying": "true"}
        track.pop("date")
    if single_dict:
        return {"recenttracks": {"track": track}}
    return {"recenttracks": {"track": [track]}}


RECENT_SCROBBLES = [
    ("Atom Bomb", "Fluke"),
    ("Absurd", "Fluke"),
    ("Born Slippy", "Underworld"),
    ("Rez", "Underworld"),
    ("Cowgirl", "Underworld"),
    ("Poison", "The Prodigy"),
    ("Breathe", "The Prodigy"),
    ("Papua New Guinea", "The Future Sound of London"),
]


def multi_recent_payload(extended=True, now_playing_first=False):
    """Eight scrobbles across four artists, newest first."""
    tracks = []
    for name, artist in RECENT_SCROBBLES:
        slug = artist.replace(" ", "+")
        if extended:
            artist_field = {"name": artist,
                            "url": f"https://www.last.fm/music/{slug}"}
        else:
            artist_field = {"mbid": "", "#text": artist}
        tracks.append({
            "artist": artist_field,
            "name": name,
            "url": f"https://www.last.fm/music/{slug}/_/{name.replace(' ', '+')}",
            "date": {"uts": "1757200000", "#text": "07 Sep 2026, 10:00"},
        })
    if now_playing_first:
        tracks[0]["@attr"] = {"nowplaying": "true"}
        tracks[0].pop("date")
    return {"recenttracks": {"track": tracks}}


def top_tracks_payload():
    return {"toptracks": {"track": [{
        "name": "Absurd",
        "playcount": "143",
        "url": "https://www.last.fm/music/Fluke/_/Absurd",
        "artist": {"name": "Fluke", "url": "https://www.last.fm/music/Fluke"},
    }]}}


def top_artists_payload():
    return {"topartists": {"artist": [{
        "name": "Underworld",
        "playcount": "1024",
        "url": "https://www.last.fm/music/Underworld",
    }]}}


class TestLoadEnvKey:
    def test_environment_variable_wins(self, tmp_path, monkeypatch):
        monkeypatch.setenv("LASTFM_API_KEY", "from-env")
        (tmp_path / ".env").write_text("LASTFM_API_KEY=from-file\n")
        assert lf.load_env_key(tmp_path) == "from-env"

    def test_falls_back_to_env_file(self, tmp_path, monkeypatch):
        monkeypatch.delenv("LASTFM_API_KEY", raising=False)
        (tmp_path / ".env").write_text(
            "OTHER=1\nLASTFM_API_KEY=\"from-file\"\n")
        assert lf.load_env_key(tmp_path) == "from-file"

    def test_blank_value_is_none(self, tmp_path, monkeypatch):
        monkeypatch.delenv("LASTFM_API_KEY", raising=False)
        (tmp_path / ".env").write_text("LASTFM_API_KEY=\n")
        assert lf.load_env_key(tmp_path) is None

    def test_missing_everywhere_is_none(self, tmp_path, monkeypatch):
        monkeypatch.delenv("LASTFM_API_KEY", raising=False)
        assert lf.load_env_key(tmp_path) is None


class TestApiUrl:
    def test_carries_method_user_key_and_json_format(self):
        url = lf.api_url("user.getrecenttracks", "sekrit")
        query = dict(
            urllib_parse_qsl(url.split("?", 1)[1]))
        assert query["method"] == "user.getrecenttracks"
        assert query["user"] == lf.USER
        assert query["api_key"] == "sekrit"
        assert query["format"] == "json"

    def test_extra_params_are_included(self):
        url = lf.api_url("user.gettoptracks", "k", period="overall", limit=1)
        query = dict(urllib_parse_qsl(url.split("?", 1)[1]))
        assert query["period"] == "overall"
        assert query["limit"] == "1"


def urllib_parse_qsl(qs):
    import urllib.parse
    return urllib.parse.parse_qsl(qs)


class TestParseLastPlayed:
    def test_maps_track_artist_and_url(self):
        got = lf.parse_last_played(recent_payload())
        assert got == {
            "track": "Atom Bomb",
            "artist": "Fluke",
            "artist_url": "https://www.last.fm/music/Fluke",
            "url": "https://www.last.fm/music/Fluke/_/Atom+Bomb",
            "now_playing": False,
        }

    def test_prefers_the_artist_url_from_the_payload(self):
        got = lf.parse_last_played(multi_recent_payload(extended=True))
        assert got["artist_url"] == "https://www.last.fm/music/Fluke"

    def test_flags_a_track_playing_right_now(self):
        assert lf.parse_last_played(recent_payload(now_playing=True))[
            "now_playing"] is True

    def test_accepts_a_single_track_object(self):
        got = lf.parse_last_played(recent_payload(single_dict=True))
        assert got["track"] == "Atom Bomb"

    def test_empty_history_is_none(self):
        assert lf.parse_last_played(recent_payload(empty=True)) is None

    def test_malformed_payload_is_none(self):
        assert lf.parse_last_played({}) is None
        assert lf.parse_last_played({"error": 10, "message": "bad key"}) is None


class TestParseTopTrack:
    def test_maps_name_artist_url_and_integer_playcount(self):
        got = lf.parse_top_track(top_tracks_payload())
        assert got == {
            "track": "Absurd",
            "artist": "Fluke",
            "artist_url": "https://www.last.fm/music/Fluke",
            "url": "https://www.last.fm/music/Fluke/_/Absurd",
            "playcount": 143,
        }

    def test_accepts_artist_as_text_variant(self):
        payload = top_tracks_payload()
        payload["toptracks"]["track"][0]["artist"] = {"#text": "Fluke"}
        assert lf.parse_top_track(payload)["artist"] == "Fluke"

    def test_empty_chart_is_none(self):
        assert lf.parse_top_track({"toptracks": {"track": []}}) is None
        assert lf.parse_top_track({}) is None


class TestParseRecentPlays:
    def test_returns_at_most_count_plays(self):
        plays = lf.parse_recent_plays(multi_recent_payload(), count=3,
                                      rng=random.Random(0))
        assert len(plays) == 3

    def test_at_most_one_play_per_artist(self):
        for seed in range(20):
            plays = lf.parse_recent_plays(multi_recent_payload(), count=5,
                                          rng=random.Random(seed))
            artists = [play["artist"] for play in plays]
            assert len(artists) == len(set(artists))

    def test_short_history_yields_fewer_plays(self):
        # Eight scrobbles but only four distinct artists.
        plays = lf.parse_recent_plays(multi_recent_payload(), count=5,
                                      rng=random.Random(0))
        assert len(plays) == 4

    def test_excludes_the_given_track(self):
        exclude = {"track": "Atom Bomb", "artist": "Fluke"}
        for seed in range(20):
            plays = lf.parse_recent_plays(multi_recent_payload(), count=5,
                                          exclude=exclude,
                                          rng=random.Random(seed))
            assert ("Atom Bomb", "Fluke") not in [
                (play["track"], play["artist"]) for play in plays]

    def test_excluding_a_track_keeps_the_artist_eligible(self):
        # Fluke's other scrobble is its only remaining candidate, so with
        # four artists and count=5 it must always be picked.
        exclude = {"track": "Atom Bomb", "artist": "Fluke"}
        for seed in range(20):
            plays = lf.parse_recent_plays(multi_recent_payload(), count=5,
                                          exclude=exclude,
                                          rng=random.Random(seed))
            fluke = [play["track"] for play in plays
                     if play["artist"] == "Fluke"]
            assert fluke == ["Absurd"]

    def test_skips_a_now_playing_entry(self):
        payload = multi_recent_payload(now_playing_first=True)
        for seed in range(20):
            plays = lf.parse_recent_plays(payload, count=5,
                                          rng=random.Random(seed))
            assert "Atom Bomb" not in [play["track"] for play in plays]

    def test_selection_varies_with_the_rng(self):
        underworld = {
            play["track"]
            for seed in range(40)
            for play in lf.parse_recent_plays(multi_recent_payload(), count=5,
                                              rng=random.Random(seed))
            if play["artist"] == "Underworld"}
        assert len(underworld) > 1

    def test_carries_track_and_artist_urls(self):
        plays = lf.parse_recent_plays(multi_recent_payload(extended=True),
                                      count=5, rng=random.Random(0))
        for play in plays:
            slug = play["artist"].replace(" ", "+")
            assert play["artist_url"] == f"https://www.last.fm/music/{slug}"
            assert play["url"].startswith("https://www.last.fm/music/")

    def test_builds_the_artist_url_when_the_payload_has_none(self):
        plays = lf.parse_recent_plays(multi_recent_payload(extended=False),
                                      count=5, rng=random.Random(0))
        by_artist = {play["artist"]: play for play in plays}
        assert by_artist["The Prodigy"]["artist_url"] == (
            "https://www.last.fm/music/The+Prodigy")

    def test_empty_or_malformed_is_an_empty_list(self):
        assert lf.parse_recent_plays({"recenttracks": {"track": []}},
                                     rng=random.Random(0)) == []
        assert lf.parse_recent_plays({}, rng=random.Random(0)) == []


class TestParseTopArtist:
    def test_maps_name_url_and_integer_playcount(self):
        got = lf.parse_top_artist(top_artists_payload())
        assert got == {
            "artist": "Underworld",
            "url": "https://www.last.fm/music/Underworld",
            "playcount": 1024,
        }

    def test_empty_chart_is_none(self):
        assert lf.parse_top_artist({"topartists": {"artist": []}}) is None
        assert lf.parse_top_artist({}) is None


class TestBuildStore:
    def test_carries_identity_timestamp_and_all_sections(self):
        store = lf.build_store(
            {"track": "Atom Bomb"}, {"track": "Absurd"},
            {"artist": "Underworld"}, [{"track": "Rez"}],
            now="2026-09-07T12:00:00+00:00")
        assert store["user"] == lf.USER
        assert store["url"] == lf.PROFILE_URL
        assert store["updated"] == "2026-09-07T12:00:00+00:00"
        assert store["last_played"] == {"track": "Atom Bomb"}
        assert store["top_track"] == {"track": "Absurd"}
        assert store["top_artist"] == {"artist": "Underworld"}
        assert store["recent_plays"] == [{"track": "Rez"}]

    def test_omits_sections_that_are_missing(self):
        store = lf.build_store(None, {"track": "Absurd"}, None, [], now="t")
        assert "last_played" not in store
        assert "top_artist" not in store
        assert "recent_plays" not in store
        assert store["top_track"] == {"track": "Absurd"}


def fake_get(url):
    if "user.getrecenttracks" in url:
        return multi_recent_payload()
    if "user.gettoptracks" in url:
        return top_tracks_payload()
    if "user.gettopartists" in url:
        return top_artists_payload()
    raise AssertionError(f"unexpected URL {url}")


class TestRun:
    def test_without_a_key_is_a_quiet_no_op(self, tmp_path):
        lines = []
        assert lf.run(tmp_path, key=None, get=fake_get, echo=lines.append) == 0
        assert not (tmp_path / lf.DATA_FILE).exists()
        assert any("LASTFM_API_KEY" in line for line in lines)

    def test_writes_the_three_stats(self, tmp_path):
        code = lf.run(tmp_path, key="k", get=fake_get,
                      echo=lambda *a, **kw: None)
        assert code == 0
        store = json.loads((tmp_path / lf.DATA_FILE).read_text())
        assert store["last_played"]["track"] == "Atom Bomb"
        assert store["top_track"]["playcount"] == 143
        assert store["top_artist"]["artist"] == "Underworld"
        assert store["updated"]

    def test_writes_a_recent_plays_sample(self, tmp_path):
        code = lf.run(tmp_path, key="k", get=fake_get,
                      echo=lambda *a, **kw: None, rng=random.Random(0))
        assert code == 0
        store = json.loads((tmp_path / lf.DATA_FILE).read_text())
        plays = store["recent_plays"]
        assert 1 <= len(plays) <= 5
        artists = [play["artist"] for play in plays]
        assert len(artists) == len(set(artists))
        for play in plays:
            assert play["artist_url"].startswith("https://www.last.fm/music/")

    def test_recent_plays_never_repeat_the_last_played_track(self, tmp_path):
        for seed in range(20):
            lf.run(tmp_path, key="k", get=fake_get,
                   echo=lambda *a, **kw: None, rng=random.Random(seed))
            store = json.loads((tmp_path / lf.DATA_FILE).read_text())
            last = (store["last_played"]["track"],
                    store["last_played"]["artist"])
            assert last not in [(play["track"], play["artist"])
                                for play in store["recent_plays"]]

    def test_fetch_failure_keeps_the_existing_file(self, tmp_path):
        data = tmp_path / lf.DATA_FILE
        data.parent.mkdir(parents=True)
        data.write_text('{"user": "old"}')

        def broken(url):
            raise OSError("network down")

        code = lf.run(tmp_path, key="k", get=broken,
                      echo=lambda *a, **kw: None)
        assert code == 1
        assert json.loads(data.read_text()) == {"user": "old"}

    def test_fetch_failure_writes_the_error_sentinel(self, tmp_path):
        def broken(url):
            raise OSError("network down")

        lf.run(tmp_path, key="k", get=broken, echo=lambda *a, **kw: None)
        sentinel = json.loads((tmp_path / lf.ERROR_FILE).read_text())
        assert "network down" in sentinel["error"]
        assert sentinel["at"]

    def test_successful_fetch_clears_the_sentinel(self, tmp_path):
        sentinel = tmp_path / lf.ERROR_FILE
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        sentinel.write_text('{"error": "old failure", "at": "t"}')
        assert lf.run(tmp_path, key="k", get=fake_get,
                      echo=lambda *a, **kw: None) == 0
        assert not sentinel.exists()

    def test_no_key_skip_leaves_the_sentinel_alone(self, tmp_path):
        # A skipped fetch says nothing about the API: the last real attempt
        # failed, and the build should keep saying so.
        sentinel = tmp_path / lf.ERROR_FILE
        sentinel.parent.mkdir(parents=True, exist_ok=True)
        sentinel.write_text('{"error": "old failure", "at": "t"}')
        assert lf.run(tmp_path, key=None, get=fake_get,
                      echo=lambda *a, **kw: None) == 0
        assert sentinel.exists()

    def test_one_bad_endpoint_keeps_the_existing_file(self, tmp_path):
        data = tmp_path / lf.DATA_FILE
        data.parent.mkdir(parents=True)
        data.write_text('{"user": "old"}')

        def flaky(url):
            if "user.gettopartists" in url:
                raise OSError("boom")
            return fake_get(url)

        code = lf.run(tmp_path, key="k", get=flaky,
                      echo=lambda *a, **kw: None)
        assert code == 1
        assert json.loads(data.read_text()) == {"user": "old"}
