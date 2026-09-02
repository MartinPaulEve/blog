"""Behavioural tests for the webmention fetch script (run from the blog root):

    uv run --with pytest -m pytest _tests/test_fetch_webmentions.py
"""

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_webmentions"))

import fetch_webmentions as fw


def entry(**overrides):
    base = {
        "type": "entry",
        "wm-id": 101,
        "wm-property": "in-reply-to",
        "wm-target": "https://eve.gd/2026/01/01/a-post/",
        "wm-received": "2026-02-01T09:00:00Z",
        "url": "https://example.org/reply",
        "published": "2026-02-01T08:30:00Z",
        "author": {"type": "card", "name": "Alice",
                   "url": "https://example.org", "photo": "https://example.org/a.png"},
        "content": {"text": "A thoughtful reply.", "html": "<p>A thoughtful reply.</p>"},
    }
    base.update(overrides)
    return base


no_avatar = lambda url: None


class TestTargetPath:
    def test_maps_full_url_to_site_relative_path(self):
        assert fw.target_path("https://eve.gd/2026/01/01/a-post/") == "/2026/01/01/a-post/"

    def test_accepts_http_and_www_variants(self):
        assert fw.target_path("http://www.eve.gd/2026/01/01/a-post/") == "/2026/01/01/a-post/"

    def test_adds_missing_trailing_slash(self):
        assert fw.target_path("https://eve.gd/2026/01/01/a-post") == "/2026/01/01/a-post/"

    def test_strips_query_and_fragment(self):
        assert fw.target_path("https://eve.gd/a-post/?utm=x#comment") == "/a-post/"

    def test_percent_encodes_non_ascii_like_jekyll(self):
        assert fw.target_path("https://eve.gd/2013/07/17/zum-gerät/") == \
            "/2013/07/17/zum-ger%C3%A4t/"

    def test_keeps_existing_percent_encoding(self):
        assert fw.target_path("https://eve.gd/2013/07/17/zum-ger%C3%A4t/") == \
            "/2013/07/17/zum-ger%C3%A4t/"

    def test_rejects_other_domains(self):
        assert fw.target_path("https://example.org/2026/01/01/a-post/") is None


class TestClassify:
    @pytest.mark.parametrize("prop,kind", [
        ("like-of", "likes"),
        ("repost-of", "reposts"),
        ("in-reply-to", "replies"),
        ("mention-of", "mentions"),
        ("bookmark-of", "bookmarks"),
    ])
    def test_maps_wm_property_to_kind(self, prop, kind):
        assert fw.classify(entry(**{"wm-property": prop})) == kind

    def test_unknown_property_counts_as_mention(self):
        assert fw.classify(entry(**{"wm-property": "rsvp"})) == "mentions"


class TestSimplify:
    def test_keeps_the_fields_templates_render(self):
        simple = fw.simplify(entry(), no_avatar)
        assert simple["wm_id"] == 101
        assert simple["url"] == "https://example.org/reply"
        assert simple["author_name"] == "Alice"
        assert simple["author_url"] == "https://example.org"
        assert simple["published"] == "2026-02-01T08:30:00Z"
        assert simple["text"] == "A thoughtful reply."

    def test_avatar_resolver_supplies_local_path(self):
        simple = fw.simplify(entry(), lambda url: "/images/webmentions/abc.png")
        assert simple["avatar"] == "/images/webmentions/abc.png"

    def test_missing_fields_degrade_gracefully(self):
        bare = entry(author={}, content=None, published=None, url=None)
        simple = fw.simplify(bare, no_avatar)
        assert simple["author_name"] == ""
        assert simple["text"] == ""
        assert simple["url"] == ""
        assert simple["published"] == "2026-02-01T09:00:00Z"  # wm-received fallback
        assert simple["avatar"] is None

    def test_truncates_very_long_text(self):
        long = entry(content={"text": "x" * 10000})
        assert len(fw.simplify(long, no_avatar)["text"]) <= fw.MAX_TEXT + 1


class TestMerge:
    def test_groups_entries_by_target_and_kind(self):
        store = fw.merge(dict(fw.EMPTY_STORE), [
            entry(),
            entry(**{"wm-id": 102, "wm-property": "like-of"}),
        ], no_avatar)
        target = store["targets"]["/2026/01/01/a-post/"]
        assert len(target["replies"]) == 1
        assert len(target["likes"]) == 1
        assert target["reposts"] == []

    def test_replaces_duplicates_by_wm_id(self):
        store = fw.merge(dict(fw.EMPTY_STORE), [entry()], no_avatar)
        updated = entry(content={"text": "Edited reply."})
        store = fw.merge(store, [updated], no_avatar)
        replies = store["targets"]["/2026/01/01/a-post/"]["replies"]
        assert len(replies) == 1
        assert replies[0]["text"] == "Edited reply."

    def test_keeps_existing_entries_on_incremental_merge(self):
        store = fw.merge(dict(fw.EMPTY_STORE), [entry()], no_avatar)
        store = fw.merge(store, [entry(**{"wm-id": 102, "wm-property": "like-of"})],
                         no_avatar)
        target = store["targets"]["/2026/01/01/a-post/"]
        assert len(target["replies"]) == 1
        assert len(target["likes"]) == 1

    def test_drops_targets_outside_the_site(self):
        store = fw.merge(dict(fw.EMPTY_STORE),
                         [entry(**{"wm-target": "https://example.org/x/"})], no_avatar)
        assert store["targets"] == {}

    def test_sorts_replies_by_published_ascending(self):
        older = entry(**{"wm-id": 1}, published="2026-01-01T00:00:00Z")
        newer = entry(**{"wm-id": 2}, published="2026-03-01T00:00:00Z")
        store = fw.merge(dict(fw.EMPTY_STORE), [newer, older], no_avatar)
        replies = store["targets"]["/2026/01/01/a-post/"]["replies"]
        assert [r["wm_id"] for r in replies] == [1, 2]

    def test_advances_last_wm_id(self):
        store = fw.merge(dict(fw.EMPTY_STORE),
                         [entry(**{"wm-id": 7}), entry(**{"wm-id": 42})], no_avatar)
        assert store["last_wm_id"] == 42


class TestFetchAll:
    def page(self, children):
        return 200, {}, json.dumps({"type": "feed", "children": children}).encode()

    def test_paginates_until_a_short_page(self):
        calls = []

        def get(url):
            calls.append(url)
            if len(calls) == 1:
                return self.page([entry(**{"wm-id": i}) for i in range(fw.PER_PAGE)])
            return self.page([entry(**{"wm-id": 999})])

        entries = fw.fetch_all(get, "tok")
        assert len(entries) == fw.PER_PAGE + 1
        assert len(calls) == 2
        assert "&page=0" in calls[0] and "&page=1" in calls[1]

    def test_sends_token_and_since_id(self):
        calls = []

        def get(url):
            calls.append(url)
            return self.page([])

        fw.fetch_all(get, "seekrit", since_id=42)
        assert "token=seekrit" in calls[0]
        assert "since_id=42" in calls[0]

    def test_api_error_raises(self):
        with pytest.raises(RuntimeError, match="500"):
            fw.fetch_all(lambda url: (500, {}, b"boom"), "tok")


class TestCacheAvatar:
    def test_downloads_once_and_returns_site_path(self, tmp_path):
        calls = []

        def get(url):
            calls.append(url)
            return 200, {"Content-Type": "image/png"}, b"\x89PNG fake"

        first = fw.cache_avatar("https://example.org/a.png", tmp_path, get)
        second = fw.cache_avatar("https://example.org/a.png", tmp_path, get)
        assert first == second
        assert first.startswith("/images/webmentions/") and first.endswith(".png")
        assert len(calls) == 1, "second call served from disk"
        assert (tmp_path / first.rsplit("/", 1)[1]).read_bytes() == b"\x89PNG fake"

    def test_failed_download_returns_none(self, tmp_path):
        assert fw.cache_avatar("https://example.org/a.png", tmp_path,
                               lambda url: (404, {}, b"")) is None

    def test_no_url_returns_none(self, tmp_path):
        assert fw.cache_avatar("", tmp_path, lambda url: (200, {}, b"")) is None


class TestLoadEnvToken:
    def test_reads_environment_first(self, tmp_path, monkeypatch):
        monkeypatch.setenv("WEBMENTION_IO_TOKEN", "from-env")
        assert fw.load_env_token(tmp_path) == "from-env"

    def test_falls_back_to_dotenv_file(self, tmp_path, monkeypatch):
        monkeypatch.delenv("WEBMENTION_IO_TOKEN", raising=False)
        (tmp_path / ".env").write_text(
            'KCWORKS_API_TOKEN=other\nWEBMENTION_IO_TOKEN="from-file"\n')
        assert fw.load_env_token(tmp_path) == "from-file"

    def test_no_token_anywhere_is_none(self, tmp_path, monkeypatch):
        monkeypatch.delenv("WEBMENTION_IO_TOKEN", raising=False)
        assert fw.load_env_token(tmp_path) is None


class TestRun:
    def api(self, children):
        return 200, {}, json.dumps({"type": "feed", "children": children}).encode()

    def seed(self, root):
        (root / "_data").mkdir()
        (root / "images" / "webmentions").mkdir(parents=True)

    def test_without_token_is_a_no_op_success(self, tmp_path):
        self.seed(tmp_path)
        code = fw.run(tmp_path, get=None, token=None, echo=lambda *a: None)
        assert code == 0
        assert not (tmp_path / fw.DATA_FILE).exists()

    def test_writes_merged_store(self, tmp_path):
        self.seed(tmp_path)
        code = fw.run(tmp_path, get=lambda url: self.api([entry()]), token="tok",
                      echo=lambda *a: None)
        assert code == 0
        store = json.loads((tmp_path / fw.DATA_FILE).read_text())
        assert "/2026/01/01/a-post/" in store["targets"]
        assert store["last_wm_id"] == 101
        assert store["updated"] is not None

    def test_incremental_fetch_passes_last_wm_id(self, tmp_path):
        self.seed(tmp_path)
        (tmp_path / fw.DATA_FILE).write_text(json.dumps(
            {"updated": "x", "last_wm_id": 55, "targets": {}}))
        calls = []

        def get(url):
            calls.append(url)
            return self.api([])

        fw.run(tmp_path, get=get, token="tok", echo=lambda *a: None)
        assert "since_id=55" in calls[0]

    def test_full_refetch_ignores_previous_state(self, tmp_path):
        self.seed(tmp_path)
        (tmp_path / fw.DATA_FILE).write_text(json.dumps(
            {"updated": "x", "last_wm_id": 55,
             "targets": {"/gone/": {"likes": [], "reposts": [], "replies": [],
                                    "mentions": [], "bookmarks": []}}}))
        calls = []

        def get(url):
            calls.append(url)
            return self.api([entry()])

        fw.run(tmp_path, get=get, token="tok", full=True, echo=lambda *a: None)
        store = json.loads((tmp_path / fw.DATA_FILE).read_text())
        assert "since_id" not in calls[0]
        assert "/gone/" not in store["targets"], "full refetch rebuilds from scratch"

    def test_api_failure_returns_nonzero_and_keeps_old_store(self, tmp_path):
        self.seed(tmp_path)
        (tmp_path / fw.DATA_FILE).write_text(json.dumps(
            {"updated": "x", "last_wm_id": 55, "targets": {}}))

        def get(url):
            return 500, {}, b"boom"

        code = fw.run(tmp_path, get=get, token="tok", echo=lambda *a: None)
        assert code != 0
        store = json.loads((tmp_path / fw.DATA_FILE).read_text())
        assert store["last_wm_id"] == 55
