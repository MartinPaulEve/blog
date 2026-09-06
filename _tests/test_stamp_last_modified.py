"""Behavioural tests for last_modified_at stamping (run from the blog root):

    uv run --with pytest -m pytest _tests/test_stamp_last_modified.py
"""

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_references"))

import stamp_last_modified as slm

POST = """---
title: "A post"
layout: post
date: 2011-12-30 20:28:53 +0100
doi: https://doi.org/10.59348/zz9cj-fwd10
references:
- https://example.org/x # A thing
---
Body text.
"""


class TestStampLastModified:
    def test_inserts_after_the_date_line(self):
        result = slm.stamp_last_modified(POST, "2026-09-06")
        assert (
            "date: 2011-12-30 20:28:53 +0100\n"
            "last_modified_at: 2026-09-06\n"
        ) in result

    def test_replaces_an_existing_value(self):
        once = slm.stamp_last_modified(POST, "2026-09-06")
        twice = slm.stamp_last_modified(once, "2026-10-01")
        assert "last_modified_at: 2026-10-01\n" in twice
        assert twice.count("last_modified_at") == 1

    def test_is_idempotent_for_the_same_date(self):
        once = slm.stamp_last_modified(POST, "2026-09-06")
        assert slm.stamp_last_modified(once, "2026-09-06") == once

    def test_appends_to_front_matter_when_no_date_line(self):
        post = "---\ntitle: x\n---\nBody\n"
        result = slm.stamp_last_modified(post, "2026-09-06")
        front = result.split("---\n")[1]
        assert "last_modified_at: 2026-09-06\n" in front
        assert result.endswith("---\nBody\n")

    def test_body_is_untouched(self):
        result = slm.stamp_last_modified(POST, "2026-09-06")
        assert result.endswith("---\nBody text.\n")

    def test_no_front_matter_raises(self):
        with pytest.raises(ValueError):
            slm.stamp_last_modified("Plain.\n", "2026-09-06")
