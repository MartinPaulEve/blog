"""Behavioural tests for the category apply/merge scripts (run from the blog root):

    uv run --with pyyaml --with pytest -m pytest _tests/test_apply_categories.py
"""

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_categorization"))

import apply_categories
import merge_batches


# --- Fixtures: era-representative post files -------------------------------

FM_2007 = """---
archive: https://wayback.archive-it.org/22123/xyz
categories:
- Technology
- InfoSec
- .NET
comments: []
date: 2007-05-15 16:06:22 +0200
date_gmt: 2007-05-15 16:06:22 +0200
doi: https://doi.org/10.59348/2zhsq-kgd29
image:
  feature: geek.png
layout: post
ogImage: images/geek.png
published: true
status: publish
tags:
- information security
- .NET
title: Amendments to the British Computer Misuse Act
wordpress_id: 289
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/example"
---

Body text here.

categories: this colon-line in the body must never be touched.
"""

FM_2015_INLINE = """---
archive: https://wayback.archive-it.org/22123/abc
categories: []
date: 2015-11-21
layout: post
tags: []
title: 'HE Green Paper: response to question 1'
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/example2"
---

Body.
"""

FM_2022_NOKEY = """---
archive: https://wayback.archive-it.org/22123/def
date: 2022-01-01
doi: https://doi.org/10.59348/hyfz7-pkm08
image:
  feature: header_email.png
layout: post
title: Last year I spent 506 hours answering emails.
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/example3"
---

Body.
"""

FM_2026_COMMENTS = """---
archive: https://wayback.archive-it.org/22123/ghi
date: 2026-08-31
layout: post
title: "On (not) using ‘AI detectors’"
references:
- https://doi.org/10.1000/x  # Eve, Open Access and the Humanities
- https://doi.org/10.1000/y  # A second comment
tags:
- AI
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/example4"
---

Body.
"""

FM_TAGS_BEFORE_CATS = """---
tags:
- one
- two
categories:
- Old Thing
title: Ordering test
---

Body.
"""

FM_INLINE_SCALAR = """---
categories: Technology
title: Scalar test
---

Body.
"""

TAXONOMY = ["Open Access", "Politics", "Information Security", "Programming",
            "Higher Education", "Personal", "Health"]


def _fm(text):
    """The front-matter section of a post file's text."""
    end = text.index("---", 3)
    return text[: end + 4]


# --- replace_categories_block ----------------------------------------------

class TestReplaceCategoriesBlock:
    def test_replaces_existing_block(self):
        out = apply_categories.replace_categories_block(
            FM_2007, ["Information Security", "Politics"])
        assert "- Information Security\n- Politics\n" in _fm(out)
        assert "- Technology\n" not in _fm(out)
        # the tags list keeps its own "- .NET" entry; only the categories
        # block loses it
        assert _fm(out).count("- .NET\n") == 1

    def test_everything_outside_block_is_byte_identical(self):
        out = apply_categories.replace_categories_block(
            FM_2007, ["Information Security"])
        assert apply_categories.strip_categories_block(out) == \
            apply_categories.strip_categories_block(FM_2007)

    def test_adjacent_keys_survive(self):
        out = apply_categories.replace_categories_block(
            FM_2007, ["Information Security"])
        assert "comments: []\n" in out
        assert "tags:\n- information security\n- .NET\n" in out
        assert 'atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/example"\n' in out
        assert "date: 2007-05-15 16:06:22 +0200\n" in out

    def test_replaces_inline_empty_list(self):
        out = apply_categories.replace_categories_block(
            FM_2015_INLINE, ["Higher Education"])
        assert "categories:\n- Higher Education\n" in _fm(out)
        assert "categories: []" not in out
        assert "tags: []\n" in out  # the neighbouring inline list is untouched

    def test_replaces_inline_scalar(self):
        out = apply_categories.replace_categories_block(
            FM_INLINE_SCALAR, ["Programming"])
        assert "categories:\n- Programming\n" in _fm(out)
        assert "categories: Technology" not in out

    def test_inserts_when_key_absent(self):
        out = apply_categories.replace_categories_block(
            FM_2022_NOKEY, ["Personal"])
        fm = _fm(out)
        assert "categories:\n- Personal\n" in fm
        # inserted at the end of the front matter, after the final key
        assert fm.index("atUri:") < fm.index("categories:")
        assert out.endswith("Body.\n")

    def test_body_categories_line_untouched(self):
        out = apply_categories.replace_categories_block(
            FM_2007, ["Information Security"])
        assert "categories: this colon-line in the body must never be touched." in out

    def test_preserves_smart_quotes_and_yaml_comments(self):
        out = apply_categories.replace_categories_block(
            FM_2026_COMMENTS, ["Open Access"])
        assert "# Eve, Open Access and the Humanities" in out
        assert "‘AI detectors’" in out
        assert "tags:\n- AI\n" in out

    def test_tags_before_categories_ordering(self):
        out = apply_categories.replace_categories_block(
            FM_TAGS_BEFORE_CATS, ["Politics"])
        assert "tags:\n- one\n- two\n" in out
        assert "categories:\n- Politics\n" in out
        assert "- Old Thing" not in out

    def test_idempotent(self):
        once = apply_categories.replace_categories_block(FM_2007, ["Politics"])
        twice = apply_categories.replace_categories_block(once, ["Politics"])
        assert once == twice

    def test_crlf_rejected(self):
        with pytest.raises(ValueError):
            apply_categories.replace_categories_block(
                FM_2007.replace("\n", "\r\n"), ["Politics"])

    def test_missing_front_matter_rejected(self):
        with pytest.raises(ValueError):
            apply_categories.replace_categories_block("No front matter here.\n", ["Politics"])


# --- validate_mapping -------------------------------------------------------

def _record(file="2007-05-15-a.md", new=None, old=None):
    return {"file": file, "title": "t", "old": [] if old is None else old,
            "new": ["Politics"] if new is None else new,
            "needs_review": False, "note": ""}


class TestValidateMapping:
    def test_valid_mapping_passes(self):
        errors = apply_categories.validate_mapping(
            [_record()], TAXONOMY, ["2007-05-15-a.md"])
        assert errors == []

    def test_unknown_category_rejected(self):
        errors = apply_categories.validate_mapping(
            [_record(new=["Blogging"])], TAXONOMY, ["2007-05-15-a.md"])
        assert any("Blogging" in e for e in errors)

    def test_zero_categories_rejected(self):
        errors = apply_categories.validate_mapping(
            [_record(new=[])], TAXONOMY, ["2007-05-15-a.md"])
        assert errors

    def test_four_categories_rejected(self):
        errors = apply_categories.validate_mapping(
            [_record(new=["Politics", "Personal", "Health", "Open Access"])],
            TAXONOMY, ["2007-05-15-a.md"])
        assert errors

    def test_duplicate_category_within_post_rejected(self):
        errors = apply_categories.validate_mapping(
            [_record(new=["Politics", "Politics"])], TAXONOMY, ["2007-05-15-a.md"])
        assert errors

    def test_unknown_file_rejected(self):
        errors = apply_categories.validate_mapping(
            [_record(file="1999-01-01-nope.md")], TAXONOMY, ["2007-05-15-a.md"])
        assert any("1999-01-01-nope.md" in e for e in errors)

    def test_post_missing_from_mapping_rejected(self):
        errors = apply_categories.validate_mapping(
            [_record()], TAXONOMY, ["2007-05-15-a.md", "2008-01-01-b.md"])
        assert any("2008-01-01-b.md" in e for e in errors)

    def test_duplicate_filename_rejected(self):
        errors = apply_categories.validate_mapping(
            [_record(), _record()], TAXONOMY, ["2007-05-15-a.md"])
        assert errors


# --- apply_mapping ----------------------------------------------------------

class TestApplyMapping:
    def _posts_dir(self, tmp_path):
        posts = tmp_path / "_posts"
        posts.mkdir()
        (posts / "2007-05-15-a.md").write_text(FM_2007, encoding="utf-8")
        (posts / "2022-01-01-b.md").write_text(FM_2022_NOKEY, encoding="utf-8")
        return posts

    def test_applies_and_is_idempotent(self, tmp_path):
        posts = self._posts_dir(tmp_path)
        records = [_record(file="2007-05-15-a.md", new=["Information Security"]),
                   _record(file="2022-01-01-b.md", new=["Personal"])]
        changed = apply_categories.apply_mapping(records, str(posts))
        assert sorted(changed) == ["2007-05-15-a.md", "2022-01-01-b.md"]
        text = (posts / "2022-01-01-b.md").read_text(encoding="utf-8")
        assert "categories:\n- Personal\n" in text
        changed_again = apply_categories.apply_mapping(records, str(posts))
        assert changed_again == []

    def test_dry_run_writes_nothing(self, tmp_path):
        posts = self._posts_dir(tmp_path)
        before = (posts / "2007-05-15-a.md").read_text(encoding="utf-8")
        records = [_record(file="2007-05-15-a.md", new=["Politics"])]
        would_change = apply_categories.apply_mapping(records, str(posts), dry_run=True)
        assert would_change == ["2007-05-15-a.md"]
        assert (posts / "2007-05-15-a.md").read_text(encoding="utf-8") == before

    def test_self_check_refuses_corrupting_write(self, tmp_path, monkeypatch):
        posts = self._posts_dir(tmp_path)
        before = (posts / "2007-05-15-a.md").read_text(encoding="utf-8")

        def corrupting(text, categories):
            return text.replace("doi:", "dio:").replace(
                "- Technology", "- " + categories[0])

        monkeypatch.setattr(apply_categories, "replace_categories_block", corrupting)
        records = [_record(file="2007-05-15-a.md", new=["Politics"])]
        with pytest.raises(Exception):
            apply_categories.apply_mapping(records, str(posts))
        assert (posts / "2007-05-15-a.md").read_text(encoding="utf-8") == before


# --- merge_batches ----------------------------------------------------------

class TestMergeBatches:
    def test_merges_and_sorts(self):
        b1 = {"prompt_version": 1, "batch": "batch-2010-1",
              "posts": [_record(file="2010-02-02-b.md")]}
        b2 = {"prompt_version": 1, "batch": "batch-2007-1",
              "posts": [_record(file="2007-05-15-a.md")]}
        merged = merge_batches.merge_batches([b1, b2])
        assert [r["file"] for r in merged] == ["2007-05-15-a.md", "2010-02-02-b.md"]

    def test_duplicate_across_batches_rejected(self):
        b1 = {"prompt_version": 1, "batch": "x", "posts": [_record()]}
        b2 = {"prompt_version": 1, "batch": "y", "posts": [_record()]}
        with pytest.raises(ValueError):
            merge_batches.merge_batches([b1, b2])

    def test_review_lists_posts_under_each_category(self):
        records = [_record(file="2007-05-15-a.md", new=["Politics", "Health"]),
                   _record(file="2010-02-02-b.md", new=["Health"])]
        review = merge_batches.render_review(records, TAXONOMY, {})
        politics_section = review.split("### Politics")[1].split("###")[0]
        assert "2007-05-15-a.md" in politics_section
        assert "2010-02-02-b.md" not in politics_section
        health_section = review.split("### Health")[1].split("###")[0]
        assert "2007-05-15-a.md" in health_section
        assert "2010-02-02-b.md" in health_section

    def test_review_flags_conflicts_and_needs_review(self):
        conflicted = _record(file="2007-05-15-a.md", new=["Health"], old=["politics"])
        flagged = dict(_record(file="2010-02-02-b.md"), needs_review=True, note="unsure")
        review = merge_batches.render_review(
            [conflicted, flagged], TAXONOMY, {"politics": "Politics"})
        assert "2007-05-15-a.md" in review.split("## Conflicts")[1]
        assert "2010-02-02-b.md" in review.split("## Needs review")[1]

    def test_review_no_conflict_when_old_overlaps_after_remap(self):
        agreeing = _record(file="2007-05-15-a.md", new=["Politics"], old=["politics"])
        review = merge_batches.render_review(
            [agreeing], TAXONOMY, {"politics": "Politics"})
        assert "2007-05-15-a.md" not in review.split("## Conflicts")[1]
