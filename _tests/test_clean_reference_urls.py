"""Behavioural tests for reference URL cleaning (run from the blog root):

    uv run --with pytest -m pytest _tests/test_clean_reference_urls.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_references"))

import clean_reference_urls as cru


class TestCleanReferenceUrl:
    def test_amazon_affiliate_link_collapses_to_dp_asin(self):
        url = (
            "http://www.amazon.co.uk/gp/product/1551303698/ref=as_li_ss_tl"
            "?ie=UTF8&tag=2bitpienet-21&linkCode=as2&camp=1634&creative=19450"
            "&creativeASIN=1551303698"
        )
        assert cru.clean_reference_url(url) == (
            "http://www.amazon.co.uk/dp/1551303698"
        )

    def test_amazon_dp_link_with_ref_suffix_is_canonicalised(self):
        url = "https://www.amazon.com/dp/B01N5IB20Q/ref=sr_1_1?keywords=x&tag=aff-20"
        assert cru.clean_reference_url(url) == "https://www.amazon.com/dp/B01N5IB20Q"

    def test_amzn_short_link_uses_resolved_target(self):
        resolved = "https://www.amazon.co.uk/Password-Object-Lessons/dp/1501314874/ref=x?tag=aff-21"
        assert cru.clean_reference_url("http://amzn.to/2abBhmD", resolved) == (
            "https://www.amazon.co.uk/dp/1501314874"
        )

    def test_amzn_short_link_without_resolution_is_kept(self):
        assert cru.clean_reference_url("http://amzn.to/2abBhmD", None) == (
            "http://amzn.to/2abBhmD"
        )

    def test_utm_parameters_are_stripped_preserving_others(self):
        url = "https://example.org/a?utm_source=feed&id=3&utm_campaign=x"
        assert cru.clean_reference_url(url) == "https://example.org/a?id=3"

    def test_clean_urls_pass_through(self):
        assert cru.clean_reference_url("https://example.org/a") == "https://example.org/a"
        assert cru.clean_reference_url("https://doi.org/10.1000/x") == "https://doi.org/10.1000/x"


POST = """---
title: "A post"
references:
- http://www.amazon.co.uk/gp/product/1551303698/ref=x?tag=aff-21 # Newson and Polster, Academic Callings
- author: Kerry Eustice
  title: A review
  url: https://example.org/a?utm_source=feed&id=3
---
Body mentions http://www.amazon.co.uk/gp/product/1551303698/ref=x?tag=aff-21 too.
"""


class TestRewriteReferenceUrls:
    MAPPING = {
        "http://www.amazon.co.uk/gp/product/1551303698/ref=x?tag=aff-21":
            "http://www.amazon.co.uk/dp/1551303698",
        "https://example.org/a?utm_source=feed&id=3":
            "https://example.org/a?id=3",
    }

    def test_bare_line_url_is_replaced_and_label_kept(self):
        result = cru.rewrite_reference_urls(POST, self.MAPPING)
        assert (
            "- http://www.amazon.co.uk/dp/1551303698 "
            "# Newson and Polster, Academic Callings\n"
        ) in result

    def test_structured_url_value_is_replaced(self):
        result = cru.rewrite_reference_urls(POST, self.MAPPING)
        assert "  url: https://example.org/a?id=3\n" in result

    def test_body_urls_are_untouched(self):
        result = cru.rewrite_reference_urls(POST, self.MAPPING)
        assert result.endswith(
            "Body mentions http://www.amazon.co.uk/gp/product/1551303698/ref=x?tag=aff-21 too.\n"
        )

    def test_unmapped_text_unchanged(self):
        assert cru.rewrite_reference_urls(POST, {}) == POST
