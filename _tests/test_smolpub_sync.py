"""Behavioural tests for the smol.pub gemtext mirror (run from the blog root):

    uv run --with pyyaml --with pytest -m pytest _tests/test_smolpub_sync.py
"""

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_smolpub"))

import sync_smolpub as sm


# --- helpers ---------------------------------------------------------------


def gem(html):
    return sm.html_to_gemtext(html)


def lines(html):
    return gem(html).splitlines()


PAGE = """<!DOCTYPE html><html><body>
<header class="header"><nav>Menu</nav></header>
<main>
<div class="post-content">
  <div class="container">
    <div class="post-body e-content">
      <p>First.</p>
      <div class="language-python highlighter-rouge"><div class="highlight"><pre class="highlight"><code>x = 1</code></pre></div></div>
      <p>Last.</p>
    </div>
    <aside class="post-sidebar"><div class="sidebar-widget">Chrome</div></aside>
  </div>
</div>
</main>
<footer class="footer">Foot</footer>
</body></html>"""


# --- extract_post_body -------------------------------------------------------


def test_body_extraction_keeps_nested_divs_and_drops_sidebar():
    body = sm.extract_post_body(PAGE)
    assert "<p>First.</p>" in body
    assert "<p>Last.</p>" in body
    assert "x = 1" in body
    assert "Chrome" not in body
    assert "Menu" not in body
    assert "Foot" not in body


def test_body_extraction_fails_loudly_without_a_post_body():
    with pytest.raises(ValueError):
        sm.extract_post_body("<html><body><p>nothing</p></body></html>")


# --- html_to_gemtext: text -------------------------------------------------


def test_paragraphs_become_single_text_lines_separated_by_blanks():
    out = gem("<p>One\n  two.</p>\n<p>Three.</p>")
    assert out.split("\n\n") == ["One two.", "Three."]


def test_inline_formatting_is_flattened_to_plain_text():
    assert gem("<p>A <em>b</em> <strong>c</strong> <code>d</code> <i>e</i>.</p>") == "A b c d e."


def test_entities_are_decoded():
    assert gem("<p>Tom &amp; Jerry &#8217;s &lt;tag&gt;</p>") == "Tom & Jerry ’s <tag>"


def test_line_breaks_split_text_lines():
    assert lines("<p>one<br>two<br />three</p>") == ["one", "two", "three"]


def test_hard_rule_is_a_blank_line_only():
    assert gem("<p>a</p><hr><p>b</p>").split("\n\n") == ["a", "b"]


def test_empty_paragraphs_and_whitespace_only_text_vanish():
    assert gem("<p></p>\n\n<p>  </p><p>x</p>") == "x"


# --- headings ---------------------------------------------------------------


def test_h1_and_h2_become_level_two_headings():
    assert gem("<h1>Top</h1>") == "## Top"
    assert gem('<h2 id="x">Section</h2>') == "## Section"


def test_h3_and_deeper_become_level_three_headings():
    assert gem("<h3>A</h3>") == "### A"
    assert gem("<h4>B</h4>") == "### B"
    assert gem("<h6>C</h6>") == "### C"


def test_heading_links_are_not_emitted_as_link_lines():
    out = gem('<h2><a href="https://x.example/">Linked</a> heading</h2>')
    assert out == "## Linked heading"


# --- links -----------------------------------------------------------------


def test_paragraph_links_follow_the_paragraph_as_link_lines():
    out = lines('<p>See <a href="https://a.example/x">the thing</a> and '
                '<a href="https://b.example/">another</a>.</p>')
    assert out == [
        "See the thing and another.",
        "=> https://a.example/x the thing",
        "=> https://b.example/ another",
    ]


def test_relative_links_are_made_absolute_against_the_site():
    out = lines('<p><a href="/2024/01/09/slug/">post</a></p>')
    assert out[1] == "=> https://eve.gd/2024/01/09/slug/ post"


def test_fragment_only_links_are_dropped():
    assert lines('<p>Jump <a href="#section">down</a>.</p>') == ["Jump down."]


def test_duplicate_link_targets_within_a_paragraph_are_listed_once():
    out = lines('<p><a href="https://a.example/">one</a> '
                '<a href="https://a.example/">two</a></p>')
    assert out == ["one two", "=> https://a.example/ one"]


def test_link_without_text_falls_back_to_the_url():
    assert lines('<p>x <a href="https://a.example/"></a></p>') == [
        "x", "=> https://a.example/"]


def test_mailto_links_are_kept():
    out = lines('<p><a href="mailto:a@b.example">mail</a></p>')
    assert out[1] == "=> mailto:a@b.example mail"


# --- images, iframes -------------------------------------------------------


def test_images_become_link_lines_to_the_eve_gd_copy_with_alt_text():
    assert lines('<p><img src="/images/health.png" alt="My health" /></p>') == [
        "=> https://eve.gd/images/health.png Image: My health"]


def test_image_without_alt_text_is_still_a_link_line():
    assert lines('<img src="https://cdn.example/a.png">') == [
        "=> https://cdn.example/a.png Image"]


def test_linked_image_yields_one_link_line_per_target():
    out = lines('<p><a href="/images/big.png"><img src="/images/small.png" '
                'alt="pic" /></a></p>')
    assert out == [
        "=> https://eve.gd/images/small.png Image: pic",
        "=> https://eve.gd/images/big.png",
    ]


def test_iframes_become_link_lines():
    assert lines('<iframe src="https://video.example/embed/1"></iframe>') == [
        "=> https://video.example/embed/1 Embedded content"]


# --- lists -----------------------------------------------------------------


def test_unordered_lists_become_star_items():
    assert lines("<ul><li>a</li><li>b <em>c</em></li></ul>") == ["* a", "* b c"]


def test_ordered_lists_are_numbered_text_lines():
    assert lines("<ol><li>a</li><li>b</li></ol>") == ["1. a", "2. b"]


def test_nested_lists_are_flattened():
    out = lines("<ul><li>a<ul><li>b</li></ul></li><li>c</li></ul>")
    assert out == ["* a", "* b", "* c"]


def test_list_item_links_follow_the_list():
    out = lines('<ul><li><a href="https://a.example/">a</a></li>'
                '<li>b</li></ul>')
    assert out == ["* a", "* b", "=> https://a.example/ a"]


def test_paragraphs_inside_list_items_stay_on_the_item_line():
    assert lines("<ul><li><p>a</p></li><li><p>b</p></li></ul>") == ["* a", "* b"]


# --- quotes ------------------------------------------------------------------


def test_blockquote_paragraphs_become_quote_lines():
    out = gem("<blockquote><p>one</p><p>two</p></blockquote>")
    assert out.split("\n\n") == ["> one", "> two"]


def test_blockquote_without_paragraphs_is_a_quote_line():
    assert gem("<blockquote>bare</blockquote>") == "> bare"


def test_blockquote_links_follow_the_quote():
    out = lines('<blockquote><p>q <a href="https://a.example/">src</a></p></blockquote>')
    assert out == ["> q src", "=> https://a.example/ src"]


# --- preformatted ----------------------------------------------------------


def test_pre_blocks_are_fenced_and_keep_whitespace():
    out = gem("<pre><code>def f():\n    return 1\n</code></pre>")
    assert out == "```\ndef f():\n    return 1\n```"


def test_highlighted_code_loses_its_spans_and_decodes_entities():
    html = ('<figure class="highlight"><pre><code class="language-html">'
            '<span class="nt">&lt;p&gt;</span>hi &amp; bye</code></pre></figure>')
    assert gem(html) == "```\n<p>hi & bye\n```"


def test_rouge_wrapped_code_is_fenced_once():
    html = ('<div class="language-python highlighter-rouge"><div class="highlight">'
            '<pre class="highlight"><code>x = <span class="mi">1</span>\n</code></pre>'
            '</div></div>')
    assert gem(html) == "```\nx = 1\n```"


def test_whitespace_inside_pre_is_not_collapsed():
    assert gem("<pre>a   b\n\n  c</pre>") == "```\na   b\n\n  c\n```"


# --- tables ------------------------------------------------------------------


def test_table_rows_become_pipe_joined_text_lines():
    html = ("<table><tr><th>A</th><th>B</th></tr>"
            "<tr><td>1</td><td>2</td></tr></table>")
    assert lines(html) == ["A | B", "1 | 2"]


def test_table_links_follow_the_table():
    html = ('<table><tr><td>Derrida</td><td><a href="/derrida/x.pdf">PDF</a></td></tr>'
            '</table>')
    assert lines(html) == ["Derrida | PDF", "=> https://eve.gd/derrida/x.pdf PDF"]


# --- footnotes ---------------------------------------------------------------


FOOTNOTED = """<p>Claim.<sup id="fnref:1"><a href="#fn:1" class="footnote" rel="footnote" role="doc-noteref">1</a></sup> More.</p>
<div class="footnotes" role="doc-endnotes">
  <ol>
    <li id="fn:1">
      <p>Jones, <em>PLOS</em>, doi:<a href="https://doi.org/10.1/x">10.1/x</a>. <a href="#fnref:1" class="reversefootnote" role="doc-backlink">&#8617;</a></p>
    </li>
  </ol>
</div>"""


def test_footnote_references_become_bracketed_numbers_inline():
    assert lines(FOOTNOTED)[0] == "Claim.[1] More."


def test_footnotes_section_lists_numbered_notes_with_their_links():
    out = lines(FOOTNOTED)
    assert "[1] Jones, PLOS, doi:10.1/x." in out
    assert "=> https://doi.org/10.1/x 10.1/x" in out
    assert not any("↩" in line for line in out)
    assert not any("fnref" in line for line in out)


def test_footnotes_section_has_a_heading():
    assert any(line.startswith("## ") for line in lines(FOOTNOTED)[1:])


# --- dropped and transparent elements ----------------------------------------


def test_scripts_styles_and_hidden_elements_are_dropped():
    html = ('<p>keep</p><script>var x = 1;</script><style>p{}</style>'
            '<ol hidden><li>no</li></ol>'
            '<p class="post-references-picker" data-ref-picker hidden>'
            '<label>Citation style:</label></p>')
    assert gem(html) == "keep"


def test_reference_list_keeps_only_the_visible_style():
    html = ('<section class="post-references"><h2 id="references">References</h2>'
            '<ol class="post-references-list" data-ref-style="mhra">'
            '<li>Eve, <i>Book</i> &lt;<a href="https://a.example/">https://a.example/</a>&gt;</li></ol>'
            '<ol class="post-references-list" data-ref-style="apa" hidden>'
            '<li>Eve (2020). Book.</li></ol></section>')
    assert lines(html) == [
        "## References",
        "",
        "1. Eve, Book <https://a.example/>",
        "=> https://a.example/",
    ]


def test_content_warning_disclosure_keeps_heading_and_label():
    html = ('<details class="content-warning"><summary>'
            '<h3 id="x">Dysmotility (2019-)</h3> '
            '<span class="cw-label">Content warning: discusses bowels</span>'
            '</summary><p>Body.</p></details>')
    out = [line for line in lines(html) if line]
    assert out == ["### Dysmotility (2019-)", "Content warning: discusses bowels", "Body."]


def test_figure_captions_are_text_lines():
    html = ('<figure><img src="/images/a.png" alt="A"><figcaption>Caption '
            'text</figcaption></figure>')
    assert [line for line in lines(html) if line] == [
        "=> https://eve.gd/images/a.png Image: A", "Caption text"]


def test_bare_text_outside_any_block_is_kept():
    assert gem("Just text") == "Just text"


def test_nested_paragraph_in_blockquote_in_paragraph_legacy_markup():
    html = "<p><blockquote>Quoted.</blockquote></p>"
    assert gem(html) == "> Quoted."


def test_output_never_has_three_consecutive_newlines():
    out = gem("<p>a</p>\n\n\n<div>\n\n</div>\n\n<p>b</p><ul></ul><p>c</p>")
    assert "\n\n\n" not in out
    assert out.split("\n\n") == ["a", "b", "c"]


# --- document assembly ------------------------------------------------------


META = {
    "title": "Rusting Away (or: packing the Crossref database)",
    "url": "https://eve.gd/2024/01/09/rusting-away/",
    "date_published": "2024-01-09",
    "date_modified": "2026-09-06",
}


def test_document_starts_with_title_heading_and_blank_line():
    doc = sm.render_document(META, "Body line.")
    first, second = doc.splitlines()[:2]
    assert first == "# Rusting Away (or: packing the Crossref database)"
    assert second == ""


def test_document_carries_provenance_date_and_web_link():
    doc = sm.render_document(META, "Body line.")
    assert "2024" in doc and "January" in doc
    assert "=> https://eve.gd/2024/01/09/rusting-away/" in doc
    assert doc.rstrip().endswith("Body line.")


def test_document_mentions_an_update_date_only_when_present():
    with_mod = sm.render_document(META, "x")
    without = sm.render_document({**META, "date_modified": None}, "x")
    assert "2026" in with_mod
    assert "2026" not in without


def test_split_document_returns_title_and_content_without_heading():
    doc = sm.render_document(META, "Body line.")
    title, content = sm.split_document(doc)
    assert title == META["title"]
    assert not content.startswith("#")
    assert content.rstrip().endswith("Body line.")
    assert "# Rusting" not in content


# --- slugs and hashes -------------------------------------------------------


def test_slug_is_lowercased_and_restricted_to_url_safe_characters():
    assert sm.smol_slug("REF-consultation") == "ref-consultation"
    assert sm.smol_slug("getting-free_cite-running") == "getting-free-cite-running"
    assert sm.smol_slug("plain-slug") == "plain-slug"


def test_slug_collapses_runs_and_trims_hyphens():
    assert sm.smol_slug("a__b--c-") == "a-b-c"


def test_content_hash_is_stable_and_content_sensitive():
    assert sm.content_hash("abc") == sm.content_hash("abc")
    assert sm.content_hash("abc") != sm.content_hash("abd")
    assert len(sm.content_hash("abc")) >= 32


# --- collecting built posts --------------------------------------------------


def make_site(tmp_path, *posts, extra_pages=(), sources=True):
    site = tmp_path / "_site"
    for (y, m, d, slug, title) in posts:
        if sources:
            posts_dir = tmp_path / "_posts"
            posts_dir.mkdir(exist_ok=True)
            (posts_dir / f"{y}-{m}-{d}-{slug}.md").write_text(
                f"---\ntitle: {title}\nlayout: post\ndate: {y}-{m}-{d}\n"
                f"doi: https://doi.org/10.1/{slug}\nkcworks: https://works/{slug}\n"
                f"---\n\n{title} body\n")
        page = site / y / m / d / slug
        page.mkdir(parents=True)
        (page / "index.html").write_text(
            f'<html><body><div class="post-body e-content"><p>{title} body</p>'
            f'</div><aside class="post-sidebar"></aside></body></html>')
        (page / "metadata.json").write_text(json.dumps({
            "@type": "BlogPosting", "name": title,
            "url": f"https://eve.gd/{y}/{m}/{d}/{slug}/",
            "datePublished": f"{y}-{m}-{d}", "dateModified": "2026-09-06",
        }))
    for rel in extra_pages:
        page = site / rel
        page.mkdir(parents=True)
        (page / "index.html").write_text("<html><body><p>page</p></body></html>")
    return site


def test_collect_posts_reads_metadata_and_body_for_each_post(tmp_path):
    site = make_site(tmp_path,
                     ("2024", "01", "09", "rusting-away", "Rusting Away"),
                     ("2016", "02", "18", "REF-consultation", "The REF"))
    posts = {p["url_slug"]: p for p in sm.collect_posts(site)}
    assert set(posts) == {"rusting-away", "REF-consultation"}
    assert posts["rusting-away"]["title"] == "Rusting Away"
    assert posts["rusting-away"]["url"] == "https://eve.gd/2024/01/09/rusting-away/"
    assert posts["rusting-away"]["date_published"] == "2024-01-09"
    assert posts["rusting-away"]["date_modified"] == "2026-09-06"
    assert "Rusting Away body" in posts["rusting-away"]["body_html"]


def test_collect_posts_ignores_non_post_pages(tmp_path):
    site = make_site(tmp_path, ("2024", "01", "09", "a", "A"),
                     extra_pages=("about", "thoughts/2026-09", "categories/x"))
    assert [p["url_slug"] for p in sm.collect_posts(site)] == ["a"]


def test_collect_posts_fails_without_a_built_site(tmp_path):
    with pytest.raises(FileNotFoundError):
        sm.collect_posts(tmp_path / "_site")


# --- planning what to push ----------------------------------------------------


DOCS = [
    {"url_slug": "a", "slug": "a", "title": "A", "content": "A text"},
    {"url_slug": "B_x", "slug": "b-x", "title": "B", "content": "B text"},
]


def ledger_for(*entries):
    return {url_slug: {"slug": slug, "hash": sm.content_hash(text), "synced": "2026-10-01"}
            for url_slug, slug, text in entries}


def test_plan_pushes_everything_when_ledger_is_empty():
    assert [d["url_slug"] for d in sm.plan_sync(DOCS, {})] == ["a", "B_x"]


def test_plan_skips_posts_whose_content_hash_is_unchanged():
    ledger = ledger_for(("a", "a", "A text"))
    assert [d["url_slug"] for d in sm.plan_sync(DOCS, ledger)] == ["B_x"]


def test_plan_includes_posts_whose_content_changed():
    ledger = ledger_for(("a", "a", "OLD"), ("B_x", "b-x", "B text"))
    assert [d["url_slug"] for d in sm.plan_sync(DOCS, ledger)] == ["a"]


def test_plan_force_pushes_unchanged_posts_too():
    ledger = ledger_for(("a", "a", "A text"), ("B_x", "b-x", "B text"))
    assert [d["url_slug"] for d in sm.plan_sync(DOCS, ledger, force=True)] == ["a", "B_x"]


def test_plan_only_restricts_to_named_slugs_regardless_of_ledger():
    ledger = ledger_for(("a", "a", "A text"))
    picked = sm.plan_sync(DOCS, ledger, only=["a"])
    assert [d["url_slug"] for d in picked] == ["a"]
    picked = sm.plan_sync(DOCS, ledger, only=["b-x"])
    assert [d["url_slug"] for d in picked] == ["B_x"]


# --- publishing ---------------------------------------------------------------


class FakeHttp:
    """Records form posts; answers with scripted statuses per URL suffix."""

    def __init__(self, statuses):
        self.statuses = statuses
        self.calls = []

    def __call__(self, url, fields, token):
        self.calls.append({"url": url, "fields": dict(fields), "token": token})
        for suffix, status in self.statuses.items():
            if url.endswith(suffix):
                return status
        return 500


def test_publish_creates_a_new_post_through_save():
    http = FakeHttp({"/posts/save": 302})
    result = sm.publish("my-slug", "Title", "content", "tok", http)
    assert result == "created"
    assert http.calls[0]["url"] == "https://smol.pub/posts/save"
    assert http.calls[0]["fields"] == {"title": "Title", "slug": "my-slug", "content": "content"}
    assert http.calls[0]["token"] == "tok"


def test_publish_falls_back_to_update_when_save_is_refused():
    http = FakeHttp({"/posts/save": 200, "/posts/my-slug/update": 302})
    assert sm.publish("my-slug", "Title", "content", "tok", http) == "updated"
    assert http.calls[1]["url"] == "https://smol.pub/posts/my-slug/update"
    assert http.calls[1]["fields"]["content"] == "content"


def test_publish_accepts_2xx_from_update():
    http = FakeHttp({"/posts/save": 200, "/posts/my-slug/update": 200})
    assert sm.publish("my-slug", "Title", "content", "tok", http) == "updated"


def test_publish_raises_when_both_endpoints_fail():
    http = FakeHttp({"/posts/save": 500, "/posts/my-slug/update": 500})
    with pytest.raises(sm.SmolPubError):
        sm.publish("my-slug", "Title", "content", "tok", http)


def test_publish_can_go_straight_to_update_for_known_posts():
    http = FakeHttp({"/posts/my-slug/update": 302})
    assert sm.publish("my-slug", "Title", "content", "tok", http, known=True) == "updated"
    assert len(http.calls) == 1


def test_multipart_encoding_carries_every_field():
    content_type, body = sm.encode_multipart({"title": "T", "slug": "s", "content": "a\nb"})
    assert content_type.startswith("multipart/form-data; boundary=")
    boundary = content_type.split("boundary=", 1)[1]
    assert boundary.encode() in body
    for name, value in (("title", "T"), ("slug", "s"), ("content", "a\nb")):
        assert f'name="{name}"'.encode() in body
        assert value.encode() in body
    assert body.endswith(b"--\r\n")


# --- ledger and token -------------------------------------------------------


def test_update_ledger_records_slug_hash_and_date_without_mutating_input():
    ledger = {"a": {"slug": "a", "hash": "old", "synced": "2026-01-01"}}
    out = sm.update_ledger(ledger, "B_x", "b-x", "h2", "2026-10-11")
    assert out["B_x"] == {"slug": "b-x", "hash": "h2", "synced": "2026-10-11"}
    assert out["a"] == ledger["a"]
    assert "B_x" not in ledger


def test_token_comes_from_the_environment_first(tmp_path):
    (tmp_path / ".env").write_text("SMOL_PUB_KEY=from-file\n")
    assert sm.load_token(tmp_path, env={"SMOL_PUB_KEY": "from-env"}) == "from-env"


def test_token_falls_back_to_the_env_file(tmp_path):
    (tmp_path / ".env").write_text("OTHER=x\nSMOL_PUB_KEY='from-file'\n")
    assert sm.load_token(tmp_path, env={}) == "from-file"


def test_missing_token_is_none(tmp_path):
    assert sm.load_token(tmp_path, env={}) is None


# --- end-to-end through main -------------------------------------------------


def test_dry_run_writes_gemtext_files_and_touches_nothing_else(tmp_path, monkeypatch):
    make_site(tmp_path, ("2024", "01", "09", "a", "A"))
    monkeypatch.chdir(tmp_path)
    http = FakeHttp({})
    code = sm.main(["--dry-run"], http=http, env={})
    assert code == 0
    assert (tmp_path / "_smolpub" / "out" / "a.gmi").read_text().startswith("# A\n\n")
    assert http.calls == []
    assert not (tmp_path / "_smolpub" / "synced.yml").exists()


def test_real_run_pushes_new_posts_and_writes_the_ledger(tmp_path, monkeypatch):
    make_site(tmp_path, ("2024", "01", "09", "a", "A"), ("2016", "02", "18", "B_x", "B"))
    monkeypatch.chdir(tmp_path)
    http = FakeHttp({"/posts/save": 302})
    assert sm.main([], http=http, env={"SMOL_PUB_KEY": "tok"}) == 0
    assert sorted(c["fields"]["slug"] for c in http.calls) == ["a", "b-x"]
    import yaml
    ledger = yaml.safe_load((tmp_path / "_smolpub" / "synced.yml").read_text())
    assert set(ledger) == {"a", "B_x"}
    assert ledger["B_x"]["slug"] == "b-x"
    assert ledger["a"]["hash"]


def test_second_run_sends_nothing_when_unchanged(tmp_path, monkeypatch):
    make_site(tmp_path, ("2024", "01", "09", "a", "A"))
    monkeypatch.chdir(tmp_path)
    http = FakeHttp({"/posts/save": 302, "/posts/a/update": 302})
    sm.main([], http=http, env={"SMOL_PUB_KEY": "tok"})
    first = len(http.calls)
    sm.main([], http=http, env={"SMOL_PUB_KEY": "tok"})
    assert len(http.calls) == first


def test_changed_post_is_updated_in_place(tmp_path, monkeypatch):
    site = make_site(tmp_path, ("2024", "01", "09", "a", "A"))
    monkeypatch.chdir(tmp_path)
    http = FakeHttp({"/posts/save": 302, "/posts/a/update": 302})
    sm.main([], http=http, env={"SMOL_PUB_KEY": "tok"})
    page = site / "2024" / "01" / "09" / "a" / "index.html"
    page.write_text(page.read_text().replace("A body", "A revised body"))
    sm.main([], http=http, env={"SMOL_PUB_KEY": "tok"})
    assert http.calls[-1]["url"].endswith("/posts/a/update")
    assert "revised" in http.calls[-1]["fields"]["content"]


def test_missing_token_fails_before_any_network(tmp_path, monkeypatch):
    make_site(tmp_path, ("2024", "01", "09", "a", "A"))
    monkeypatch.chdir(tmp_path)
    http = FakeHttp({"/posts/save": 302})
    assert sm.main([], http=http, env={}) != 0
    assert http.calls == []


def test_failed_push_leaves_that_post_out_of_the_ledger_and_exits_nonzero(tmp_path, monkeypatch):
    make_site(tmp_path, ("2024", "01", "09", "a", "A"), ("2024", "01", "10", "b", "B"))
    monkeypatch.chdir(tmp_path)

    class Flaky(FakeHttp):
        def __call__(self, url, fields, token):
            super().__call__(url, fields, token)
            return 302 if fields["slug"] == "a" else 500

    code = sm.main([], http=Flaky({}), env={"SMOL_PUB_KEY": "tok"})
    assert code != 0
    import yaml
    ledger = yaml.safe_load((tmp_path / "_smolpub" / "synced.yml").read_text())
    assert set(ledger) == {"a"}


def test_slug_transliterates_accented_letters():
    assert sm.smol_slug("notes-on-les-encres-noires-au-moyen-âge") == "notes-on-les-encres-noires-au-moyen-age"
    assert sm.smol_slug("from-s-gerät-to-y-gerät") == "from-s-gerat-to-y-gerat"


def test_text_lines_that_look_like_gemtext_markup_are_escaped():
    out = lines("<p>#AcBoWriMo starts today</p><p>=&gt; not a link</p>"
                "<p>* not a bullet</p><p>```not a fence</p>")
    assert out == [" #AcBoWriMo starts today", "", " => not a link", "",
                   " * not a bullet", "", " ```not a fence"]


def test_text_lines_starting_with_a_quote_marker_are_left_alone():
    assert gem("<p>&gt; 50% of readers</p>") == "> 50% of readers"


def test_collect_posts_skips_built_pages_whose_source_post_is_gone(tmp_path):
    site = make_site(tmp_path, ("2024", "01", "09", "a", "A"), ("2015", "02", "06", "stale", "S"),
                     sources=False)
    posts = tmp_path / "_posts"
    posts.mkdir()
    (posts / "2024-01-09-a.md").write_text("---\ntitle: A\n---\nbody\n")
    assert [p["url_slug"] for p in sm.collect_posts(site, posts_dir=posts)] == ["a"]


def test_collect_posts_without_a_posts_dir_takes_every_built_post(tmp_path):
    site = make_site(tmp_path, ("2024", "01", "09", "a", "A"), ("2015", "02", "06", "b", "B"),
                     sources=False)
    assert len(sm.collect_posts(site, posts_dir=tmp_path / "nowhere")) == 2


def test_collect_posts_falls_back_to_the_page_when_metadata_json_is_missing(tmp_path):
    page = tmp_path / "_site" / "2021" / "08" / "19" / "s-gerät"
    page.mkdir(parents=True)
    page.joinpath("index.html").write_text(
        '<html><body><h1 class="post-title p-name">S-Gerät &amp; friends</h1>'
        '<time itemprop="datePublished" datetime="2021-08-19">August 19, 2021</time>'
        '(last updated <time itemprop="dateModified" datetime="2026-09-06">x</time>)'
        '<div class="post-body e-content"><p>Body</p></div></body></html>')
    [post] = sm.collect_posts(tmp_path / "_site")
    assert post["url_slug"] == "s-gerät"
    assert post["title"] == "S-Gerät & friends"
    assert post["url"] == "https://eve.gd/2021/08/19/s-gerät/"
    assert post["date_published"] == "2021-08-19"
    assert post["date_modified"] == "2026-09-06"


def test_link_urls_with_non_ascii_characters_are_percent_encoded():
    out = lines('<p><a href="/2021/08/19/s-gerät/">post</a></p>')
    assert out[1] == "=> https://eve.gd/2021/08/19/s-ger%C3%A4t/ post"


def test_document_web_link_is_percent_encoded():
    doc = sm.render_document({**META, "url": "https://eve.gd/2021/08/19/s-gerät/"}, "x")
    assert "=> https://eve.gd/2021/08/19/s-ger%C3%A4t/ " in doc
    assert "gerät/ Read" not in doc


# --- front-matter stamping ----------------------------------------------------


FM_FULL = """---
title: "A post"
layout: post
date: 2026-08-28
doi: https://doi.org/10.59348/mjvdw-w0051
roguescholar: https://rogue-scholar.org/records/26jfx-f4w16
kcworks: https://works.hcommons.org/records/83n59-ana25
biron: https://eprints.bbk.ac.uk/id/eprint/57592/
image:
  feature: metadatatiles.jpg
---

Body mentioning biron: and smolpub: inline.
"""

FM_DOI_ONLY = """---
title: "Older"
date: 2007-05-15
doi: https://doi.org/10.59348/2zhsq-kgd29
comments: []
---

Old body.
"""


def test_stamp_inserts_smolpub_key_after_the_biron_line():
    out = sm.stamp_front_matter(FM_FULL, "a-post")
    lines = out.splitlines()
    biron = lines.index("biron: https://eprints.bbk.ac.uk/id/eprint/57592/")
    assert lines[biron + 1] == "smolpub: a-post"


def test_stamp_falls_back_to_kcworks_then_doi_then_end_of_front_matter():
    out = sm.stamp_front_matter(FM_DOI_ONLY, "older")
    lines = out.splitlines()
    assert lines[lines.index("doi: https://doi.org/10.59348/2zhsq-kgd29") + 1] == "smolpub: older"
    out = sm.stamp_front_matter("---\ntitle: x\n---\n\nBody.\n", "x")
    assert out == "---\ntitle: x\nsmolpub: x\n---\n\nBody.\n"


def test_stamp_is_idempotent_and_replaces_an_existing_value():
    once = sm.stamp_front_matter(FM_FULL, "a-post")
    assert sm.stamp_front_matter(once, "a-post") == once
    changed = sm.stamp_front_matter(once, "renamed")
    assert changed.split("---")[1].count("smolpub:") == 1
    assert "smolpub: renamed" in changed


def test_stamp_leaves_body_and_other_front_matter_untouched():
    out = sm.stamp_front_matter(FM_FULL, "a-post")
    assert "Body mentioning biron: and smolpub: inline." in out
    assert "  feature: metadatatiles.jpg" in out
    assert out.count("---\n") == 2


def test_stamp_refuses_text_without_front_matter():
    with pytest.raises(ValueError):
        sm.stamp_front_matter("No front matter here.\n", "x")


def test_real_run_stamps_the_source_post_after_a_successful_push(tmp_path, monkeypatch):
    make_site(tmp_path, ("2024", "01", "09", "a", "A"), ("2016", "02", "18", "B_x", "B"))
    monkeypatch.chdir(tmp_path)
    assert sm.main([], http=FakeHttp({"/posts/save": 302}), env={"SMOL_PUB_KEY": "tok"}) == 0
    a = (tmp_path / "_posts" / "2024-01-09-a.md").read_text()
    b = (tmp_path / "_posts" / "2016-02-18-B_x.md").read_text()
    assert "smolpub: a\n" in a.split("---")[1]
    assert "smolpub: b-x\n" in b.split("---")[1]


def test_dry_run_does_not_stamp(tmp_path, monkeypatch):
    make_site(tmp_path, ("2024", "01", "09", "a", "A"))
    monkeypatch.chdir(tmp_path)
    sm.main(["--dry-run"], http=FakeHttp({}), env={})
    assert "smolpub:" not in (tmp_path / "_posts" / "2024-01-09-a.md").read_text()


def test_failed_push_leaves_the_post_unstamped(tmp_path, monkeypatch):
    make_site(tmp_path, ("2024", "01", "09", "a", "A"))
    monkeypatch.chdir(tmp_path)
    sm.main([], http=FakeHttp({}), env={"SMOL_PUB_KEY": "tok"})
    assert "smolpub:" not in (tmp_path / "_posts" / "2024-01-09-a.md").read_text()


def test_posts_already_in_the_ledger_but_unstamped_get_stamped_without_a_push(tmp_path, monkeypatch):
    make_site(tmp_path, ("2024", "01", "09", "a", "A"))
    monkeypatch.chdir(tmp_path)
    http = FakeHttp({"/posts/save": 302})
    sm.main([], http=http, env={"SMOL_PUB_KEY": "tok"})
    post = tmp_path / "_posts" / "2024-01-09-a.md"
    post.write_text(post.read_text().replace("smolpub: a\n", ""))
    sent = len(http.calls)
    assert sm.main([], http=http, env={}) == 0   # no token needed: nothing to push
    assert len(http.calls) == sent
    assert "smolpub: a\n" in post.read_text()
