"""Behavioural tests for the citation enrichment tooling (run from the blog root):

    uv run --with pyyaml --with beautifulsoup4 --with pytest -m pytest _tests/test_upgrade_references.py
"""

import pathlib
import sys

import pytest
import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_references"))

import fetch_citation_meta
import upgrade_references


class TestBareReferenceUrls:
    POST = """---
title: "A post"
references:
- https://example.org/article # An article
- http://dx.doi.org/10.1017/CBO9781316161012 # Eve 2014, OA and the Humanities
- author: Karen Coyle
  title: 'An Ontology'
  url: https://journal.code4lib.org/articles/16491
---
Body with https://example.org/body-link mentioned.
"""

    def test_returns_only_bare_non_doi_front_matter_urls(self):
        assert fetch_citation_meta.bare_reference_urls(self.POST) == [
            "https://example.org/article"
        ]

    def test_ignores_posts_without_references(self):
        assert fetch_citation_meta.bare_reference_urls("---\ntitle: x\n---\nBody\n") == []


class TestExtractPageMeta:
    def test_prefers_citation_tags_for_scholarly_pages(self):
        html = """<html><head>
        <title>Site - Article</title>
        <meta name="citation_title" content="A Study of Things">
        <meta name="citation_author" content="Jane Roe">
        <meta name="citation_author" content="John Doe">
        <meta name="citation_publication_date" content="2015/03/01">
        <meta name="citation_journal_title" content="Journal of Things">
        </head><body></body></html>"""
        meta = fetch_citation_meta.extract_page_meta(html)
        assert meta["title"] == "A Study of Things"
        assert meta["authors"] == ["Jane Roe", "John Doe"]
        assert meta["date"] == "2015/03/01"
        assert meta["site"] == "Journal of Things"

    def test_reads_opengraph_and_article_tags(self):
        html = """<html><head>
        <meta property="og:title" content="A Blog Post">
        <meta property="og:site_name" content="Some Blog">
        <meta property="og:type" content="article">
        <meta property="article:published_time" content="2014-04-01T10:00:00Z">
        </head><body></body></html>"""
        meta = fetch_citation_meta.extract_page_meta(html)
        assert meta["title"] == "A Blog Post"
        assert meta["site"] == "Some Blog"
        assert meta["type"] == "article"
        assert meta["date"].startswith("2014-04-01")

    def test_reads_json_ld_author_and_publisher(self):
        html = """<html><head><script type="application/ld+json">
        {"@type": "NewsArticle", "headline": "Big News",
         "author": {"@type": "Person", "name": "A Reporter"},
         "datePublished": "2013-05-02",
         "publisher": {"@type": "Organization", "name": "The Paper"}}
        </script></head><body></body></html>"""
        meta = fetch_citation_meta.extract_page_meta(html)
        assert meta["title"] == "Big News"
        assert meta["authors"] == ["A Reporter"]
        assert meta["date"] == "2013-05-02"
        assert meta["site"] == "The Paper"
        assert meta["type"] == "NewsArticle"

    def test_falls_back_to_title_element(self):
        html = "<html><head><title> Plain Page </title></head><body></body></html>"
        meta = fetch_citation_meta.extract_page_meta(html)
        assert meta["title"] == "Plain Page"

    def test_absent_evidence_yields_absent_keys(self):
        meta = fetch_citation_meta.extract_page_meta("<html><body>hi</body></html>")
        assert "authors" not in meta
        assert "date" not in meta


class TestCitationEntryYaml:
    def test_orders_keys_in_house_style(self):
        entry = upgrade_references.citation_entry_yaml(
            {
                "url": "https://example.org/a",
                "title": "A Study",
                "author": ["Jane Roe", "John Doe"],
                "date": "2015-03-01",
                "type": "ScholarlyArticle",
                "isPartOf": {"name": "Journal of Things", "type": "Periodical"},
            }
        )
        assert entry.index("author:") < entry.index("date:")
        assert entry.index("date:") < entry.index("title:")
        assert entry.index("type:") < entry.index("url:")
        assert entry.index("url:") < entry.index("isPartOf:")

    def test_yields_valid_yaml_list_item(self):
        entry = upgrade_references.citation_entry_yaml(
            {"url": "https://example.org/a", "title": "It's \"quoted\": tricky"}
        )
        parsed = yaml.safe_load(entry)
        assert parsed == [
            {"url": "https://example.org/a", "title": "It's \"quoted\": tricky"}
        ]

    def test_single_author_stays_scalar(self):
        entry = upgrade_references.citation_entry_yaml(
            {"url": "https://example.org/a", "author": "Jane Roe"}
        )
        assert yaml.safe_load(entry)[0]["author"] == "Jane Roe"


POST = """---
title: "A post"
layout: post
references:
- https://example.org/article # An article label
- http://dx.doi.org/10.1017/CBO9781316161012 # Eve 2014
- https://example.org/unknown # Something unfetchable
---
Body text stays.
"""

CITATIONS = {
    "https://example.org/article": {
        "title": "A Study of Things",
        "author": "Jane Roe",
        "date": "2015-03-01",
        "type": "ScholarlyArticle",
    }
}


class TestUpgradeReferencesBlock:
    def test_upgrades_bare_line_to_structured_entry(self):
        result = upgrade_references.upgrade_references_block(POST, CITATIONS)
        fm = yaml.safe_load(FRONT := result.split("---\n")[1])
        entry = fm["references"][0]
        assert entry["title"] == "A Study of Things"
        assert entry["author"] == "Jane Roe"
        assert entry["url"] == "https://example.org/article"

    def test_doi_and_unenriched_lines_keep_their_bare_form(self):
        result = upgrade_references.upgrade_references_block(POST, CITATIONS)
        assert "- http://dx.doi.org/10.1017/CBO9781316161012 # Eve 2014" in result
        assert "- https://example.org/unknown # Something unfetchable" in result

    def test_order_of_references_is_preserved(self):
        result = upgrade_references.upgrade_references_block(POST, CITATIONS)
        fm = yaml.safe_load(result.split("---\n")[1])
        urls = [
            r["url"] if isinstance(r, dict) else r for r in fm["references"]
        ]
        assert urls == [
            "https://example.org/article",
            "http://dx.doi.org/10.1017/CBO9781316161012",
            "https://example.org/unknown",
        ]

    def test_body_and_other_front_matter_untouched(self):
        result = upgrade_references.upgrade_references_block(POST, CITATIONS)
        assert result.endswith("---\nBody text stays.\n")
        assert 'title: "A post"' in result
        assert "layout: post" in result

    def test_no_citations_leaves_text_unchanged(self):
        assert upgrade_references.upgrade_references_block(POST, {}) == POST

    def test_post_without_references_unchanged(self):
        plain = "---\ntitle: x\n---\nBody\n"
        assert upgrade_references.upgrade_references_block(plain, CITATIONS) == plain

    def test_existing_structured_entries_untouched(self):
        post = """---
title: "A post"
references:
- author: Karen Coyle
  title: An Ontology
  url: https://journal.code4lib.org/articles/16491
---
Body.
"""
        assert (
            upgrade_references.upgrade_references_block(
                post, {"https://journal.code4lib.org/articles/16491": {"title": "X"}}
            )
            == post
        )
