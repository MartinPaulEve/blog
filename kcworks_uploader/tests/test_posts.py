from pathlib import Path

import pytest

from kcworks_uploader.posts import (
    canonical_url,
    find_pdf,
    first_paragraph,
    parse_post,
    post_slug,
)

POST_NAME = "2026-08-28-repository-metadata.md"

POST_TEXT = """---
title: "Repository metadata contain ontological ambiguities"
layout: post
date: 2026-08-28
doi: https://doi.org/10.59348/mjvdw-w0051
tags:
- metadata
- repositories
image:
  feature: metadatatiles.jpg
---
{% include _toc.html %}

## A heading

This is the *first* real paragraph with a [link](https://example.com) and
a continuation line.

Second paragraph here.
"""


@pytest.fixture
def post_file(tmp_path):
    path = tmp_path / POST_NAME
    path.write_text(POST_TEXT)
    return path


class TestParsePost:
    def test_extracts_title(self, post_file):
        assert parse_post(post_file).title == (
            "Repository metadata contain ontological ambiguities"
        )

    def test_normalises_date_to_iso_string(self, post_file):
        assert parse_post(post_file).date == "2026-08-28"

    def test_normalises_doi_to_bare_form(self, post_file):
        assert parse_post(post_file).doi == "10.59348/mjvdw-w0051"

    def test_extracts_tags(self, post_file):
        assert parse_post(post_file).tags == ["metadata", "repositories"]

    def test_body_excludes_front_matter(self, post_file):
        body = parse_post(post_file).body
        assert "first" in body
        assert "title:" not in body

    def test_missing_optional_fields_default_sensibly(self, tmp_path):
        path = tmp_path / "2020-01-02-plain.md"
        path.write_text("---\ntitle: Plain\n---\nBody text.\n")
        post = parse_post(path)
        assert post.doi is None
        assert post.tags == []
        # Date falls back to the one encoded in the filename.
        assert post.date == "2020-01-02"

    def test_datetime_date_is_truncated_to_date(self, tmp_path):
        path = tmp_path / "2013-07-28-timed.md"
        path.write_text(
            "---\ntitle: Timed\ndate: 2013-07-28 21:06:04\n---\nBody.\n"
        )
        assert parse_post(path).date == "2013-07-28"


class TestSlugAndUrl:
    def test_slug_is_filename_without_extension(self):
        assert post_slug(Path("/x/_posts/" + POST_NAME)) == (
            "2026-08-28-repository-metadata"
        )

    def test_canonical_url_follows_site_permalink(self):
        assert canonical_url("2026-08-28-repository-metadata") == (
            "https://eve.gd/2026/08/28/repository-metadata/"
        )


class TestFindPdf:
    def test_prefers_pdf_cache(self, tmp_path):
        (tmp_path / ".pdf_cache").mkdir()
        (tmp_path / "_site" / "PDF").mkdir(parents=True)
        cached = tmp_path / ".pdf_cache" / "slug.pdf"
        cached.write_bytes(b"%PDF")
        (tmp_path / "_site" / "PDF" / "slug.pdf").write_bytes(b"%PDF")
        assert find_pdf(tmp_path, "slug") == cached

    def test_falls_back_to_site_pdf(self, tmp_path):
        (tmp_path / "_site" / "PDF").mkdir(parents=True)
        built = tmp_path / "_site" / "PDF" / "slug.pdf"
        built.write_bytes(b"%PDF")
        assert find_pdf(tmp_path, "slug") == built

    def test_raises_when_no_pdf_exists(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            find_pdf(tmp_path, "slug")


class TestFirstParagraph:
    def test_skips_liquid_and_headings_and_cleans_markdown(self):
        body = (
            "{% include _toc.html %}\n\n## A heading\n\n"
            "This is the *first* real paragraph with a "
            "[link](https://example.com) and\na continuation line.\n\n"
            "Second paragraph here.\n"
        )
        assert first_paragraph(body) == (
            "This is the first real paragraph with a link and "
            "a continuation line."
        )

    def test_empty_body_gives_empty_string(self):
        assert first_paragraph("") == ""
