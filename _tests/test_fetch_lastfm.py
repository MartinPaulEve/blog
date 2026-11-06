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


# --- the full listening log ------------------------------------------------

import datetime

UTC = datetime.timezone.utc


def iso(ts, tz=UTC):
    return datetime.datetime.fromtimestamp(ts, tz).isoformat(timespec="seconds")


def scrobble(ts, name, artist, album="An Album", extended=True, playing=False):
    slug = artist.replace(" ", "+")
    if extended:
        artist_field = {"name": artist, "url": f"https://www.last.fm/music/{slug}"}
    else:
        artist_field = {"mbid": "", "#text": artist}
    track = {
        "artist": artist_field,
        "name": name,
        "album": {"mbid": "", "#text": album},
        "url": f"https://www.last.fm/music/{slug}/_/{name.replace(' ', '+')}",
        "date": {"uts": str(ts), "#text": "whenever"},
    }
    if playing:
        track["@attr"] = {"nowplaying": "true"}
        track.pop("date")
    return track


def scrobbles_payload(tracks, page=1, total_pages=1):
    return {"recenttracks": {
        "track": tracks,
        "@attr": {"page": str(page), "totalPages": str(total_pages),
                  "total": str(len(tracks)), "perPage": "200"},
    }}


def play(ts, name, artist="Fluke", **extra):
    slug = artist.replace(" ", "+")
    entry = {"ts": ts, "date": iso(ts), "track": name, "artist": artist,
             "artist_url": f"https://www.last.fm/music/{slug}",
             "url": f"https://www.last.fm/music/{slug}/_/{name.replace(' ', '+')}"}
    entry.update(extra)
    return entry


class TestParseScrobbles:
    def test_maps_each_play_with_its_timestamp_and_date(self):
        payload = scrobbles_payload([scrobble(1757200000, "Atom Bomb", "Fluke")])
        [got] = lf.parse_scrobbles(payload, tz=UTC)
        assert got == {
            "ts": 1757200000,
            "date": iso(1757200000),
            "track": "Atom Bomb",
            "artist": "Fluke",
            "artist_url": "https://www.last.fm/music/Fluke",
            "url": "https://www.last.fm/music/Fluke/_/Atom+Bomb",
            "album": "An Album",
        }

    def test_dates_are_written_in_the_given_zone(self):
        london = datetime.timezone(datetime.timedelta(hours=1))
        payload = scrobbles_payload([scrobble(1757200000, "Atom Bomb", "Fluke")])
        [got] = lf.parse_scrobbles(payload, tz=london)
        assert got["date"] == iso(1757200000, london)
        assert got["date"].endswith("+01:00")

    def test_keeps_the_payload_order(self):
        payload = scrobbles_payload([scrobble(300, "C", "X"), scrobble(200, "B", "X"),
                                     scrobble(100, "A", "X")])
        assert [p["track"] for p in lf.parse_scrobbles(payload, tz=UTC)] == ["C", "B", "A"]

    def test_skips_the_track_playing_right_now(self):
        payload = scrobbles_payload([scrobble(0, "Live", "X", playing=True),
                                     scrobble(100, "A", "X")])
        assert [p["track"] for p in lf.parse_scrobbles(payload, tz=UTC)] == ["A"]

    def test_a_blank_album_is_left_out(self):
        payload = scrobbles_payload([scrobble(100, "A", "X", album="")])
        [got] = lf.parse_scrobbles(payload, tz=UTC)
        assert "album" not in got

    def test_builds_the_artist_url_when_the_payload_has_none(self):
        payload = scrobbles_payload([scrobble(100, "A", "The Prodigy", extended=False)])
        [got] = lf.parse_scrobbles(payload, tz=UTC)
        assert got["artist_url"] == "https://www.last.fm/music/The+Prodigy"

    def test_empty_or_malformed_is_an_empty_list(self):
        assert lf.parse_scrobbles(scrobbles_payload([]), tz=UTC) == []
        assert lf.parse_scrobbles({}, tz=UTC) == []
        assert lf.parse_scrobbles({"recenttracks": {"track": scrobble(100, "A", "X")}},
                                  tz=UTC)[0]["track"] == "A"


class TestMergePlays:
    def test_fresh_plays_are_logged_newest_first(self):
        plays, through = lf.merge_plays([], [play(100, "A"), play(200, "B")])
        assert [p["track"] for p in plays] == ["B", "A"]
        assert through == 200

    def test_the_order_fresh_plays_arrive_in_does_not_matter(self):
        plays, _ = lf.merge_plays([], [play(200, "B"), play(100, "A")])
        assert [p["track"] for p in plays] == ["B", "A"]

    def test_the_same_track_several_times_in_a_row_is_one_entry_with_a_count(self):
        fresh = [play(100, "A"), play(200, "A"), play(300, "A"), play(400, "B")]
        plays, through = lf.merge_plays([], fresh)
        assert plays == [play(400, "B"), play(100, "A", n=3)]
        assert through == 400

    def test_a_repeat_separated_by_another_track_is_logged_again(self):
        fresh = [play(100, "A"), play(200, "B"), play(300, "A")]
        plays, _ = lf.merge_plays([], fresh)
        assert plays == [play(300, "A"), play(200, "B"), play(100, "A")]

    def test_a_run_continues_across_syncs(self):
        log = [play(100, "A", n=2)]
        plays, through = lf.merge_plays(log, [play(300, "A")], through=200)
        assert plays == [play(100, "A", n=3)]
        assert through == 300

    def test_matching_ignores_case(self):
        fresh = [play(100, "Atom Bomb", "Fluke"), play(200, "atom bomb", "FLUKE")]
        plays, _ = lf.merge_plays([], fresh)
        assert len(plays) == 1
        assert plays[0]["n"] == 2

    def test_a_different_artist_with_the_same_title_is_a_different_track(self):
        fresh = [play(100, "Blue", "X"), play(200, "Blue", "Y")]
        plays, _ = lf.merge_plays([], fresh)
        assert len(plays) == 2

    def test_plays_already_covered_by_through_are_ignored(self):
        log = [play(100, "A")]
        plays, through = lf.merge_plays(
            log, [play(100, "A"), play(50, "Z"), play(200, "C")], through=100)
        assert plays == [play(200, "C"), play(100, "A")]
        assert through == 200

    def test_duplicate_timestamps_count_once(self):
        plays, _ = lf.merge_plays([], [play(100, "A"), play(100, "A")])
        assert plays == [play(100, "A")]

    def test_nothing_new_leaves_the_log_and_through_alone(self):
        log = [play(100, "A")]
        assert lf.merge_plays(log, [], through=100) == ([play(100, "A")], 100)


class PagedGet:
    """A fake API serving a recent-tracks history in pages; records queries."""

    def __init__(self, pages, fail=False):
        self.pages = pages  # list of track lists, page 1 first
        self.queries = []
        self.fail = fail

    def __call__(self, url):
        query = dict(urllib_parse_qsl(url.split("?", 1)[1]))
        self.queries.append(query)
        if self.fail:
            raise OSError("boom")
        if query["method"] == "user.gettoptracks":
            return top_tracks_payload()
        if query["method"] == "user.gettopartists":
            return top_artists_payload()
        assert query["method"] == "user.getrecenttracks"
        if query.get("limit") != str(lf.PAGE_LIMIT):
            return multi_recent_payload()  # the sidebar widget's own fetch
        page = int(query.get("page", 1))
        if not self.pages:
            return scrobbles_payload([], page=1, total_pages=0)
        return scrobbles_payload(self.pages[page - 1], page=page,
                                 total_pages=len(self.pages))

    def log_queries(self):
        return [q for q in self.queries
                if q["method"] == "user.getrecenttracks"
                and q.get("limit") == str(lf.PAGE_LIMIT)]


class TestFetchScrobbles:
    def test_walks_every_page_newest_first(self):
        get = PagedGet([[scrobble(300, "C", "X")], [scrobble(200, "B", "X")],
                        [scrobble(100, "A", "X")]])
        tracks = lf.fetch_scrobbles("k", get=get)
        assert [t["name"] for t in tracks] == ["C", "B", "A"]
        assert [q["page"] for q in get.log_queries()] == ["1", "2", "3"]

    def test_asks_for_full_pages_with_artist_details(self):
        get = PagedGet([[scrobble(100, "A", "X")]])
        lf.fetch_scrobbles("k", get=get)
        [query] = get.log_queries()
        assert query["limit"] == "200"
        assert query["extended"] == "1"

    def test_asks_only_for_plays_after_since(self):
        get = PagedGet([[scrobble(100, "A", "X")]])
        lf.fetch_scrobbles("k", get=get, since=1757200000)
        assert all(q["from"] == "1757200000" for q in get.log_queries())

    def test_no_since_means_the_whole_history(self):
        get = PagedGet([[scrobble(100, "A", "X")]])
        lf.fetch_scrobbles("k", get=get)
        assert all("from" not in q for q in get.log_queries())

    def test_an_empty_history_is_an_empty_list(self):
        assert lf.fetch_scrobbles("k", get=PagedGet([])) == []

    def test_a_page_without_paging_attributes_is_the_only_page(self):
        get = lambda url: {"recenttracks": {"track": [scrobble(100, "A", "X")]}}
        assert [t["name"] for t in lf.fetch_scrobbles("k", get=get)] == ["A"]


class TestLoadListening:
    def test_missing_file_is_an_empty_log(self, tmp_path):
        log = lf.load_listening(tmp_path)
        assert log["plays"] == []
        assert log["through"] == 0

    def test_reads_plays_and_through_back(self, tmp_path):
        path = tmp_path / lf.LISTENING_FILE
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"plays": [play(100, "A")], "through": 100}))
        log = lf.load_listening(tmp_path)
        assert log["plays"] == [play(100, "A")]
        assert log["through"] == 100

    def test_a_corrupt_file_is_an_error_not_a_fresh_start(self, tmp_path):
        path = tmp_path / lf.LISTENING_FILE
        path.parent.mkdir(parents=True)
        path.write_text("{not json")
        import pytest
        with pytest.raises(ValueError):
            lf.load_listening(tmp_path)


def read_log(root):
    return json.loads((root / lf.LISTENING_FILE).read_text())


class TestSyncListening:
    def test_first_sync_backfills_the_whole_history(self, tmp_path):
        get = PagedGet([[scrobble(300, "C", "X"), scrobble(200, "B", "X")],
                        [scrobble(100, "A", "X")]])
        assert lf.sync_listening(tmp_path, "k", get=get, tz=UTC,
                                 echo=lambda *a: None, now="2026-11-06T12:00:00+00:00")
        log = read_log(tmp_path)
        assert [p["track"] for p in log["plays"]] == ["C", "B", "A"]
        assert log["through"] == 300
        assert log["updated"] == "2026-11-06T12:00:00+00:00"
        assert log["user"] == lf.USER
        assert log["url"] == lf.PROFILE_URL
        assert all("from" not in q for q in get.log_queries())

    def test_later_syncs_fetch_only_newer_plays_and_extend_the_log(self, tmp_path):
        first = PagedGet([[scrobble(100, "A", "X")]])
        lf.sync_listening(tmp_path, "k", get=first, tz=UTC, echo=lambda *a: None)
        second = PagedGet([[scrobble(300, "C", "X"), scrobble(200, "B", "X")]])
        assert lf.sync_listening(tmp_path, "k", get=second, tz=UTC,
                                 echo=lambda *a: None)
        assert all(q["from"] == "100" for q in second.log_queries())
        log = read_log(tmp_path)
        assert [p["track"] for p in log["plays"]] == ["C", "B", "A"]
        assert log["through"] == 300

    def test_a_run_of_one_track_is_collapsed(self, tmp_path):
        get = PagedGet([[scrobble(300, "A", "X"), scrobble(200, "A", "X"),
                         scrobble(100, "A", "X")]])
        lf.sync_listening(tmp_path, "k", get=get, tz=UTC, echo=lambda *a: None)
        log = read_log(tmp_path)
        assert len(log["plays"]) == 1
        assert log["plays"][0]["n"] == 3
        assert log["plays"][0]["ts"] == 100

    def test_nothing_new_leaves_the_file_untouched(self, tmp_path):
        lf.sync_listening(tmp_path, "k", get=PagedGet([[scrobble(100, "A", "X")]]),
                          tz=UTC, echo=lambda *a: None, now="first")
        before = (tmp_path / lf.LISTENING_FILE).read_text()
        assert lf.sync_listening(tmp_path, "k", get=PagedGet([]), tz=UTC,
                                 echo=lambda *a: None, now="second")
        assert (tmp_path / lf.LISTENING_FILE).read_text() == before

    def test_a_failed_fetch_leaves_the_log_untouched_and_is_false(self, tmp_path):
        lf.sync_listening(tmp_path, "k", get=PagedGet([[scrobble(100, "A", "X")]]),
                          tz=UTC, echo=lambda *a: None)
        before = (tmp_path / lf.LISTENING_FILE).read_text()
        lines = []
        assert lf.sync_listening(tmp_path, "k", get=PagedGet([], fail=True),
                                 tz=UTC, echo=lines.append) is False
        assert (tmp_path / lf.LISTENING_FILE).read_text() == before
        assert lines

    def test_a_corrupt_log_is_reported_not_overwritten(self, tmp_path):
        path = tmp_path / lf.LISTENING_FILE
        path.parent.mkdir(parents=True)
        path.write_text("{not json")
        assert lf.sync_listening(tmp_path, "k", get=PagedGet([[scrobble(1, "A", "X")]]),
                                 tz=UTC, echo=lambda *a: None) is False
        assert path.read_text() == "{not json"


class TestRunWithTheLog:
    def test_a_full_run_writes_the_widget_data_and_the_log(self, tmp_path):
        get = PagedGet([[scrobble(200, "B", "X"), scrobble(100, "A", "X")]])
        assert lf.run(tmp_path, key="k", get=get, echo=lambda *a, **kw: None) == 0
        assert (tmp_path / lf.DATA_FILE).exists()
        assert [p["track"] for p in read_log(tmp_path)["plays"]] == ["B", "A"]
        assert not (tmp_path / lf.ERROR_FILE).exists()

    def test_a_failed_log_sync_keeps_the_widget_data_and_flags_the_error(self, tmp_path):
        class WidgetOnly(PagedGet):
            def __call__(self, url):
                if f"limit={lf.PAGE_LIMIT}" in url:
                    raise OSError("history down")
                return super().__call__(url)

        code = lf.run(tmp_path, key="k", get=WidgetOnly([]),
                      echo=lambda *a, **kw: None)
        assert code == 1
        assert (tmp_path / lf.DATA_FILE).exists()
        assert not (tmp_path / lf.LISTENING_FILE).exists()
        assert (tmp_path / lf.ERROR_FILE).exists()
