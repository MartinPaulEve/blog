"""Behavioural tests for the references backfill tooling (run from the blog root):

    uv run --with pyyaml --with pytest -m pytest _tests/test_apply_references.py
"""

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_references"))

import apply_references
import extract_manifest


class TestExtractExternalUrls:
    def test_finds_markdown_links(self):
        body = "See [the report](https://example.org/report) for details.\n"
        assert extract_manifest.extract_external_urls(body) == [
            "https://example.org/report"
        ]

    def test_finds_html_href_links(self):
        body = 'Via <a href="http://ha.ckers.org/xss.html">this page</a>.\n'
        assert extract_manifest.extract_external_urls(body) == [
            "http://ha.ckers.org/xss.html"
        ]

    def test_finds_bare_urls_in_prose(self):
        body = "It lives at https://example.org/thing. Really.\n"
        assert extract_manifest.extract_external_urls(body) == [
            "https://example.org/thing"
        ]

    def test_unescapes_html_entities_in_hrefs(self):
        body = '<a href="https://example.org/?a=1&amp;b=2">x</a>\n'
        assert extract_manifest.extract_external_urls(body) == [
            "https://example.org/?a=1&b=2"
        ]

    def test_skips_markdown_images(self):
        body = "![alt text](https://example.org/pic.png)\n"
        assert extract_manifest.extract_external_urls(body) == []

    def test_skips_img_and_script_src(self):
        body = '<img src="https://example.org/pic.png"><script src="https://evil.example/x.js"></script>\n'
        assert extract_manifest.extract_external_urls(body) == []

    def test_skips_urls_inside_fenced_code_blocks(self):
        body = "Try:\n\n```\ncurl https://example.org/api\n```\n"
        assert extract_manifest.extract_external_urls(body) == []

    def test_skips_urls_inside_pre_and_code_tags(self):
        body = (
            "<pre>&lt;script src=http://ha.ckers.org/xss.js&gt;</pre>\n"
            "and <code>https://example.org/inline</code>\n"
        )
        assert extract_manifest.extract_external_urls(body) == []

    def test_skips_internal_links(self):
        body = (
            "[old post](https://eve.gd/2020/01/01/a-post/) and "
            "[home](https://www.eve.gd/) and "
            "[out](https://example.org/x)\n"
        )
        assert extract_manifest.extract_external_urls(body) == [
            "https://example.org/x"
        ]

    def test_deduplicates_preserving_first_appearance_order(self):
        body = (
            "[a](https://b.example/2) then [b](https://a.example/1) "
            "then [c](https://b.example/2)\n"
        )
        assert extract_manifest.extract_external_urls(body) == [
            "https://b.example/2",
            "https://a.example/1",
        ]

    def test_trims_trailing_punctuation_from_bare_urls(self):
        body = "See https://example.org/page, or (https://example.org/other).\n"
        assert extract_manifest.extract_external_urls(body) == [
            "https://example.org/page",
            "https://example.org/other",
        ]


class TestLinkContexts:
    def test_returns_link_text_and_surrounding_prose(self):
        body = "As shown in [the Science report](https://example.org/r), things happened.\n"
        contexts = extract_manifest.link_contexts(
            body, ["https://example.org/r"]
        )
        text, ctx = contexts[0]
        assert text == "the Science report"
        assert "things happened" in ctx

    def test_bare_url_has_no_link_text(self):
        body = "Available at https://example.org/r for now.\n"
        contexts = extract_manifest.link_contexts(
            body, ["https://example.org/r"]
        )
        text, ctx = contexts[0]
        assert text is None
        assert "Available at" in ctx


class TestIsAlive:
    @pytest.mark.parametrize("status", [200, 301, 401, 403, 429])
    def test_reachable_and_restricted_statuses_are_alive(self, status):
        assert apply_references.is_alive(status) is True

    @pytest.mark.parametrize("status", [404, 410, 500, 503, None])
    def test_misses_errors_and_failures_are_dead(self, status):
        assert apply_references.is_alive(status) is False


class TestFormatReferenceLine:
    def test_url_with_comment(self):
        assert apply_references.format_reference_line(
            "https://doi.org/10.1000/x", "Author, Title"
        ) == "- https://doi.org/10.1000/x # Author, Title"

    def test_url_without_comment(self):
        assert apply_references.format_reference_line(
            "https://example.org/x"
        ) == "- https://example.org/x"

    def test_comment_whitespace_is_collapsed(self):
        assert apply_references.format_reference_line(
            "https://example.org/x", "A  long\ncomment"
        ) == "- https://example.org/x # A long comment"


POST = """---
title: "A post"
layout: post
date: 2015-01-15
doi: https://doi.org/10.59348/abcde-f0123
image:
  feature: pic.png
---
Body with [a link](https://example.org/report).
"""


class TestInsertReferencesBlock:
    ENTRIES = [
        {"url": "https://example.org/report", "comment": "The report"},
        {"url": "https://doi.org/10.1000/x", "comment": None},
    ]

    def test_appends_block_inside_front_matter(self):
        result = apply_references.insert_references_block(POST, self.ENTRIES)
        front_matter = result.split("---\n")[1]
        assert (
            "references:\n"
            "- https://example.org/report # The report\n"
            "- https://doi.org/10.1000/x\n"
        ) in front_matter

    def test_body_is_byte_identical(self):
        result = apply_references.insert_references_block(POST, self.ENTRIES)
        assert result.endswith("Body with [a link](https://example.org/report).\n")

    def test_front_matter_remains_valid_yaml(self):
        yaml = pytest.importorskip("yaml")
        result = apply_references.insert_references_block(POST, self.ENTRIES)
        parsed = yaml.safe_load(result.split("---\n")[1])
        assert parsed["references"] == [
            "https://example.org/report",
            "https://doi.org/10.1000/x",
        ]

    def test_empty_entries_leave_text_unchanged(self):
        assert apply_references.insert_references_block(POST, []) == POST

    def test_existing_references_block_raises(self):
        already = POST.replace(
            "image:", "references:\n- https://example.org/x\nimage:"
        )
        with pytest.raises(ValueError):
            apply_references.insert_references_block(already, self.ENTRIES)

    def test_no_front_matter_raises(self):
        with pytest.raises(ValueError):
            apply_references.insert_references_block("Plain.\n", self.ENTRIES)
