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


class TestFindBlogRoot:
    def test_finds_config_in_start_dir(self, tmp_path):
        from kcworks_uploader.posts import find_blog_root

        (tmp_path / "_config.yml").write_text("title: t")
        assert find_blog_root(tmp_path) == tmp_path

    def test_walks_up_to_ancestor(self, tmp_path):
        from kcworks_uploader.posts import find_blog_root

        (tmp_path / "_config.yml").write_text("title: t")
        nested = tmp_path / "_posts"
        nested.mkdir()
        assert find_blog_root(nested) == tmp_path

    def test_none_when_no_config_anywhere(self, tmp_path):
        from kcworks_uploader.posts import find_blog_root

        assert find_blog_root(tmp_path / "nowhere") is None


class TestBlogCollection:
    def test_reads_the_configured_collection(self, tmp_path):
        from kcworks_uploader.posts import blog_collection

        (tmp_path / "_config.yml").write_text(
            "title: t\nkcworks_collection: evegd-blog-posts\n"
        )
        assert blog_collection(tmp_path) == "evegd-blog-posts"

    def test_none_when_key_absent(self, tmp_path):
        from kcworks_uploader.posts import blog_collection

        (tmp_path / "_config.yml").write_text("title: t\n")
        assert blog_collection(tmp_path) is None

    def test_none_when_config_missing(self, tmp_path):
        from kcworks_uploader.posts import blog_collection

        assert blog_collection(tmp_path) is None


class TestPendingPosts:
    def test_lists_posts_without_kcworks_records_in_filename_order(
        self, tmp_path
    ):
        from kcworks_uploader.posts import pending_posts

        posts = tmp_path / "_posts"
        posts.mkdir()
        (posts / "2026-02-01-b.md").write_text(
            "---\ntitle: B\nkcworks: https://works.hcommons.org/records/"
            "bbb22-bbb22\n---\nBody\n"
        )
        (posts / "2026-03-01-c.md").write_text(
            "---\ntitle: C\n---\nNo deposit here\n"
        )
        (posts / "2026-01-01-a.md").write_text(
            "---\ntitle: A\n---\nNor here\n"
        )
        assert [p.name for p in pending_posts(posts)] == [
            "2026-01-01-a.md",
            "2026-03-01-c.md",
        ]

    def test_all_deposited_gives_empty_queue(self, tmp_path):
        from kcworks_uploader.posts import pending_posts

        posts = tmp_path / "_posts"
        posts.mkdir()
        (posts / "2026-01-01-a.md").write_text(
            "---\ntitle: A\nkcworks: https://works.hcommons.org/records/"
            "aaa11-aaa11\n---\nBody\n"
        )
        assert pending_posts(posts) == []


class TestRecordDeposit:
    def test_stamps_url_into_front_matter(self, post_file):
        from kcworks_uploader.posts import record_deposit

        record_deposit(
            post_file, "https://works.hcommons.org/records/abc12-xyz34"
        )
        assert parse_post(post_file).title == (
            "Repository metadata contain ontological ambiguities"
        )
        assert (
            "kcworks: https://works.hcommons.org/records/abc12-xyz34"
            in post_file.read_text()
        )

    def test_leaves_every_other_byte_untouched(self, post_file):
        from kcworks_uploader.posts import record_deposit

        before = post_file.read_text()
        record_deposit(
            post_file, "https://works.hcommons.org/records/abc12-xyz34"
        )
        after = post_file.read_text()
        assert after.replace(
            "kcworks: https://works.hcommons.org/records/abc12-xyz34\n", ""
        ) == before

    def test_already_deposited_post_is_left_alone(self, tmp_path):
        from kcworks_uploader.posts import record_deposit

        path = tmp_path / "2026-01-01-a.md"
        original = (
            "---\ntitle: A\nkcworks: https://works.hcommons.org/records/"
            "aaa11-aaa11\n---\nBody\n"
        )
        path.write_text(original)
        record_deposit(
            path, "https://works.hcommons.org/records/other-id123"
        )
        assert path.read_text() == original

    def test_no_front_matter_raises(self, tmp_path):
        from kcworks_uploader.posts import record_deposit

        path = tmp_path / "2026-01-01-bare.md"
        path.write_text("Just some text, no front matter.\n")
        with pytest.raises(ValueError):
            record_deposit(
                path, "https://works.hcommons.org/records/abc12-xyz34"
            )


class TestDepositedRecords:
    def test_lists_posts_with_kcworks_records_in_filename_order(
        self, tmp_path
    ):
        from kcworks_uploader.posts import deposited_records

        posts = tmp_path / "_posts"
        posts.mkdir()
        (posts / "2026-02-01-b.md").write_text(
            "---\ntitle: B\nkcworks: https://works.hcommons.org/records/"
            "bbb22-bbb22\n---\nBody\n"
        )
        (posts / "2026-01-01-a.md").write_text(
            "---\ntitle: A\nkcworks: https://works.hcommons.org/records/"
            "aaa11-aaa11\n---\nBody\n"
        )
        (posts / "2026-03-01-c.md").write_text(
            "---\ntitle: C\n---\nNo deposit here\n"
        )
        records = deposited_records(posts)
        assert [(p.name, r) for p, r in records] == [
            ("2026-01-01-a.md", "aaa11-aaa11"),
            ("2026-02-01-b.md", "bbb22-bbb22"),
        ]

    def test_empty_dir_gives_no_records(self, tmp_path):
        from kcworks_uploader.posts import deposited_records

        posts = tmp_path / "_posts"
        posts.mkdir()
        assert deposited_records(posts) == []
