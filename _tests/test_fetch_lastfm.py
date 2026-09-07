"""Behavioural tests for the Last.fm fetch script (run from the blog root):

    uv run --with pytest -m pytest _tests/test_fetch_lastfm.py
"""

import json
import pathlib
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
            "url": "https://www.last.fm/music/Fluke/_/Atom+Bomb",
            "now_playing": False,
        }

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
            {"artist": "Underworld"}, now="2026-09-07T12:00:00+00:00")
        assert store["user"] == lf.USER
        assert store["url"] == lf.PROFILE_URL
        assert store["updated"] == "2026-09-07T12:00:00+00:00"
        assert store["last_played"] == {"track": "Atom Bomb"}
        assert store["top_track"] == {"track": "Absurd"}
        assert store["top_artist"] == {"artist": "Underworld"}

    def test_omits_sections_that_are_missing(self):
        store = lf.build_store(None, {"track": "Absurd"}, None, now="t")
        assert "last_played" not in store
        assert "top_artist" not in store
        assert store["top_track"] == {"track": "Absurd"}


def fake_get(url):
    if "user.getrecenttracks" in url:
        return recent_payload()
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
