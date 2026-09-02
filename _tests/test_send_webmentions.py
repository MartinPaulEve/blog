"""Behavioural tests for the webmention send script (run from the blog root):

    uv run --with pytest -m pytest _tests/test_send_webmentions.py
"""

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_webmentions"))

import send_webmentions as sw


POST_PAGE = """<html><head><title>t</title></head><body>
<article class="blog-post h-entry">
<div class="post-header"><a href="https://doi.org/10.1/self">doi</a></div>
<div class="post-content"><div class="container">
<div class="post-body e-content">
<p>See <a href="https://example.org/essay">this essay</a> and
<a href="https://other.net/page">another</a>.</p>
<div><a href="https://nested.example/deep">nested link</a></div>
<p><a href="/2020/01/01/internal/">internal</a>
<a href="mailto:x@y.z">mail</a></p>
</div>
<aside class="post-sidebar"><a href="https://sidebar.example/x">sidebar</a></aside>
</div></div>
</article></body></html>
"""


class TestExtractPostBody:
    def test_returns_inner_html_of_post_body_div_only(self):
        body = sw.extract_post_body(POST_PAGE)
        assert "this essay" in body
        assert "nested link" in body
        assert "sidebar" not in body
        assert "post-header" not in body

    def test_handles_nested_divs_correctly(self):
        body = sw.extract_post_body(POST_PAGE)
        assert "<div><a href=\"https://nested.example/deep\">" in body

    def test_page_without_post_body_is_none(self):
        assert sw.extract_post_body("<html><body><p>hi</p></body></html>") is None


class TestBodyLinks:
    def test_finds_absolute_links_in_document_order(self):
        body = sw.extract_post_body(POST_PAGE)
        assert sw.body_links(body) == [
            "https://example.org/essay",
            "https://other.net/page",
            "https://nested.example/deep",
        ]

    def test_ignores_relative_and_mailto_links(self):
        links = sw.body_links('<a href="/x/">a</a> <a href="mailto:a@b.c">b</a>')
        assert links == []

    def test_deduplicates_repeated_targets(self):
        html = ('<a href="https://example.org/x">one</a>'
                '<a href="https://example.org/x">two</a>')
        assert sw.body_links(html) == ["https://example.org/x"]


class TestEligible:
    def test_external_links_are_eligible(self):
        assert sw.eligible("https://example.org/essay") is True

    @pytest.mark.parametrize("url", [
        "https://eve.gd/2020/01/01/self/",
        "https://www.eve.gd/x/",
        "https://doi.org/10.59348/xyz",
        "https://dx.doi.org/10.1/x",
        "http://localhost:8000/x",
    ])
    def test_self_and_skip_hosts_are_not(self, url):
        assert sw.eligible(url) is False


class TestContentHash:
    def test_stable_for_identical_content(self):
        assert sw.content_hash("<p>same</p>") == sw.content_hash("<p>same</p>")

    def test_differs_when_content_changes(self):
        assert sw.content_hash("<p>one</p>") != sw.content_hash("<p>two</p>")


class TestEndpointDiscovery:
    def test_link_header_with_quoted_rel(self):
        assert sw.endpoint_from_link_header(
            '<https://wm.example/ep>; rel="webmention"',
            "https://example.org/page") == "https://wm.example/ep"

    def test_link_header_with_multiple_links_and_rels(self):
        value = ('</style.css>; rel=preload, '
                 '</webmention>; rel="webmention somethingelse"')
        assert sw.endpoint_from_link_header(value, "https://example.org/page") == \
            "https://example.org/webmention"

    def test_link_header_without_webmention_is_none(self):
        assert sw.endpoint_from_link_header(
            '<https://x>; rel="preconnect"', "https://example.org/") is None

    def test_html_link_tag_relative_href_resolves(self):
        html = '<html><head><link rel="webmention" href="/wm"></head><body></body></html>'
        assert sw.endpoint_from_html(html, "https://example.org/a/page") == \
            "https://example.org/wm"

    def test_html_anchor_rel_webmention_counts(self):
        html = '<body><a rel="webmention" href="https://ep.example/wm">wm</a></body>'
        assert sw.endpoint_from_html(html, "https://example.org/") == \
            "https://ep.example/wm"

    def test_html_without_endpoint_is_none(self):
        assert sw.endpoint_from_html("<p>nope</p>", "https://example.org/") is None

    def test_discover_prefers_header_over_html(self):
        def fetch(url):
            return (200, {"Link": '<https://hdr.example/wm>; rel="webmention"'},
                    '<link rel="webmention" href="https://html.example/wm">',
                    url)

        assert sw.discover_endpoint("https://example.org/x", fetch) == \
            "https://hdr.example/wm"

    def test_discover_resolves_html_endpoint_against_final_redirect_url(self):
        def fetch(url):
            return (200, {}, '<link rel="webmention" href="wm-ep">',
                    "https://moved.example/dir/page")

        assert sw.discover_endpoint("https://example.org/x", fetch) == \
            "https://moved.example/dir/wm-ep"

    def test_discover_fetch_error_is_none(self):
        def fetch(url):
            raise OSError("connection refused")

        assert sw.discover_endpoint("https://example.org/x", fetch) is None


class TestCollectPosts:
    def make_site(self, tmp_path):
        post = tmp_path / "_site" / "2026" / "01" / "01" / "a-post"
        post.mkdir(parents=True)
        post.joinpath("index.html").write_text(POST_PAGE)
        about = tmp_path / "_site" / "about"
        about.mkdir()
        about.joinpath("index.html").write_text(POST_PAGE)
        return tmp_path / "_site"

    def test_collects_year_dir_posts_only(self, tmp_path):
        posts = sw.collect_posts(self.make_site(tmp_path))
        assert [p["path"] for p in posts] == ["/2026/01/01/a-post/"]

    def test_post_carries_hash_and_eligible_targets(self, tmp_path):
        post = sw.collect_posts(self.make_site(tmp_path))[0]
        assert post["hash"] == sw.content_hash(sw.extract_post_body(POST_PAGE))
        assert post["targets"] == [
            "https://example.org/essay",
            "https://other.net/page",
            "https://nested.example/deep",
        ]


class TestPlan:
    def post(self, path="/2026/01/01/a-post/", hash="h1",
             targets=("https://example.org/a", "https://other.net/b")):
        return {"path": path, "hash": hash, "targets": list(targets)}

    def sent_state(self, hash="h1", targets=("https://example.org/a",
                                             "https://other.net/b")):
        return {"posts": {"/2026/01/01/a-post/": {
            "content_hash": hash,
            "sent": {t: {"at": "2026-01-01T00:00:00+00:00", "endpoint": "e"}
                     for t in targets}}}}

    def test_new_post_sends_to_every_target(self):
        actions = sw.plan({"posts": {}}, [self.post()])
        assert [(a["target"], a["reason"]) for a in actions] == [
            ("https://example.org/a", "new"), ("https://other.net/b", "new")]

    def test_unchanged_post_sends_nothing(self):
        assert sw.plan(self.sent_state(), [self.post()]) == []

    def test_unchanged_post_retries_unrecorded_target(self):
        state = self.sent_state(targets=("https://example.org/a",))
        actions = sw.plan(state, [self.post()])
        assert [(a["target"], a["reason"]) for a in actions] == [
            ("https://other.net/b", "retry")]

    def test_updated_post_resends_all_and_notifies_removed(self):
        state = self.sent_state(hash="old",
                                targets=("https://example.org/a", "https://gone.example/x"))
        actions = sw.plan(state, [self.post()])
        got = {(a["target"], a["reason"]) for a in actions}
        assert got == {("https://example.org/a", "update"),
                       ("https://other.net/b", "update"),
                       ("https://gone.example/x", "removed")}


class TestBaseline:
    def test_records_everything_without_network(self):
        posts = [{"path": "/2026/01/01/a-post/", "hash": "h1",
                  "targets": ["https://example.org/a"]}]
        state = sw.baseline({"posts": {}}, posts, now="2026-09-02T00:00:00+00:00")
        recorded = state["posts"]["/2026/01/01/a-post/"]
        assert recorded["content_hash"] == "h1"
        assert recorded["sent"]["https://example.org/a"]["baseline"] is True


class TestApply:
    def actions(self):
        return [{"source": "/2026/01/01/a-post/",
                 "target": "https://example.org/a", "reason": "new"}]

    def posts(self):
        return [{"path": "/2026/01/01/a-post/", "hash": "h1",
                 "targets": ["https://example.org/a"]}]

    def test_successful_send_is_recorded_with_endpoint(self):
        sends = []

        def post(url, data):
            sends.append((url, data))
            return 202

        state = sw.apply({"posts": {}}, self.posts(), self.actions(),
                         discover=lambda t, fetch=None: "https://wm.example/ep",
                         post=post, echo=lambda *a: None,
                         now="2026-09-02T00:00:00+00:00")
        assert sends == [("https://wm.example/ep",
                          {"source": "https://eve.gd/2026/01/01/a-post/",
                           "target": "https://example.org/a"})]
        recorded = state["posts"]["/2026/01/01/a-post/"]
        assert recorded["content_hash"] == "h1"
        assert recorded["sent"]["https://example.org/a"]["endpoint"] == \
            "https://wm.example/ep"

    def test_no_endpoint_is_recorded_so_it_is_not_reprobed(self):
        state = sw.apply({"posts": {}}, self.posts(), self.actions(),
                         discover=lambda t, fetch=None: None,
                         post=lambda u, d: pytest.fail("must not POST"),
                         echo=lambda *a: None)
        assert state["posts"]["/2026/01/01/a-post/"]["sent"][
            "https://example.org/a"]["endpoint"] is None

    def test_failed_post_is_not_recorded_for_retry_next_run(self):
        state = sw.apply({"posts": {}}, self.posts(), self.actions(),
                         discover=lambda t, fetch=None: "https://wm.example/ep",
                         post=lambda u, d: 500, echo=lambda *a: None)
        assert "https://example.org/a" not in \
            state["posts"]["/2026/01/01/a-post/"]["sent"]

    def test_removed_target_is_dropped_from_state_after_notification(self):
        state = {"posts": {"/2026/01/01/a-post/": {
            "content_hash": "old",
            "sent": {"https://gone.example/x": {"at": "x", "endpoint": "e"}}}}}
        actions = [{"source": "/2026/01/01/a-post/",
                    "target": "https://gone.example/x", "reason": "removed"}]
        posts = [{"path": "/2026/01/01/a-post/", "hash": "h2", "targets": []}]
        state = sw.apply(state, posts, actions,
                         discover=lambda t, fetch=None: "https://wm.example/ep",
                         post=lambda u, d: 200, echo=lambda *a: None)
        assert "https://gone.example/x" not in \
            state["posts"]["/2026/01/01/a-post/"]["sent"]
        assert state["posts"]["/2026/01/01/a-post/"]["content_hash"] == "h2"


class TestRun:
    def make_root(self, tmp_path):
        post = tmp_path / "_site" / "2026" / "01" / "01" / "a-post"
        post.mkdir(parents=True)
        post.joinpath("index.html").write_text(POST_PAGE)
        (tmp_path / "_webmentions").mkdir()
        return tmp_path

    def test_baseline_writes_state_without_network(self, tmp_path):
        root = self.make_root(tmp_path)
        code = sw.run(root, mode="baseline",
                      fetch=lambda url: pytest.fail("no network in baseline"),
                      post=lambda u, d: pytest.fail("no network in baseline"),
                      echo=lambda *a: None)
        assert code == 0
        state = json.loads((root / sw.STATE_FILE).read_text())
        recorded = state["posts"]["/2026/01/01/a-post/"]
        assert set(recorded["sent"]) == {"https://example.org/essay",
                                        "https://other.net/page",
                                        "https://nested.example/deep"}

    def test_dry_run_reports_but_does_not_send_or_write(self, tmp_path):
        root = self.make_root(tmp_path)
        lines = []
        code = sw.run(root, mode="dry-run",
                      fetch=lambda url: pytest.fail("no network in dry-run"),
                      post=lambda u, d: pytest.fail("no network in dry-run"),
                      echo=lines.append)
        assert code == 0
        assert not (root / sw.STATE_FILE).exists()
        assert any("example.org/essay" in line for line in lines)

    def test_send_updates_state_and_second_run_is_quiet(self, tmp_path):
        root = self.make_root(tmp_path)
        sends = []

        def fetch(url):
            return (200, {"Link": '<https://wm.example/ep>; rel="webmention"'},
                    "", url)

        def post(url, data):
            sends.append(data["target"])
            return 202

        assert sw.run(root, mode="send", fetch=fetch, post=post,
                      echo=lambda *a: None) == 0
        assert sorted(sends) == ["https://example.org/essay",
                                 "https://nested.example/deep",
                                 "https://other.net/page"]

        sends.clear()
        assert sw.run(root, mode="send", fetch=fetch, post=post,
                      echo=lambda *a: None) == 0
        assert sends == [], "an unchanged deploy sends nothing"
