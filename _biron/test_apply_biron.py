"""Tests for the BIROn post/eprint matcher.

Run from the blog root:

    uv run _biron/test_apply_biron.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apply_biron import build_mapping


def post(fname):
    year, month, day, slug = fname[:-3].split("-", 3)
    return {"file": fname, "doi": None, "path": f"/{year}/{month}/{day}/{slug}"}


def eprint(eprintid, url, title=None):
    return {
        "eprintid": eprintid,
        "uri": f"https://eprints.bbk.ac.uk/id/eprint/{eprintid}",
        "url": url,
        "doi": None,
        "title": title,
    }


class TestGreekSlugMatching(unittest.TestCase):
    def test_plain_ascii_path_still_matches(self):
        posts = [post("2012-03-01-some-ordinary-post.md")]
        eprints = [eprint(100, "https://eve.gd/2012/03/01/some-ordinary-post/")]
        mapping, _ = build_mapping(posts, eprints)
        self.assertEqual(
            mapping["2012-03-01-some-ordinary-post.md"],
            "https://eprints.bbk.ac.uk/id/eprint/100/",
        )

    def test_double_encoded_greek_url_matches_dashed_hex_slug(self):
        # BIROn holds https://eve.gd/2012/01/06/adorno-terminology-%25ce%25ac.../
        # (double-encoded); the post file spells the same Greek title as
        # dashed hex bytes with the word-separator hyphens collapsed.
        posts = [
            post("2012-01-06-adorno-terminology-ce-ac-ce-bb-ce-bb-ce-bf-ce-b3-ce-ad-ce-bd-ce-bf-cf-82.md")
        ]
        eprints = [
            eprint(
                17386,
                "https://eve.gd/2012/01/06/adorno-terminology-"
                "%25ce%25ac%25ce%25bb%25ce%25bb%25ce%25bf-"
                "%25ce%25b3%25ce%25ad%25ce%25bd%25ce%25bf%25cf%2582/",
                title="Adorno terminology: άλλο γένος",
            )
        ]
        mapping, anomalies = build_mapping(posts, eprints)
        self.assertEqual(
            mapping[posts[0]["file"]],
            "https://eprints.bbk.ac.uk/id/eprint/17386/",
        )
        self.assertEqual(anomalies, [])

    def test_single_encoded_greek_url_matches_too(self):
        posts = [
            post("2012-01-06-adorno-terminology-ce-ac-ce-bb-ce-bb-ce-bf-ce-b3-ce-ad-ce-bd-ce-bf-cf-82.md")
        ]
        eprints = [
            eprint(
                17386,
                "https://eve.gd/2012/01/06/adorno-terminology-"
                "%ce%ac%ce%bb%ce%bb%ce%bf-%ce%b3%ce%ad%ce%bd%ce%bf%cf%82/",
            )
        ]
        mapping, _ = build_mapping(posts, eprints)
        self.assertEqual(
            mapping[posts[0]["file"]],
            "https://eprints.bbk.ac.uk/id/eprint/17386/",
        )

    def test_literal_greek_url_matches_too(self):
        posts = [
            post("2012-01-06-adorno-terminology-ce-ac-ce-bb-ce-bb-ce-bf-ce-b3-ce-ad-ce-bd-ce-bf-cf-82.md")
        ]
        eprints = [eprint(17386, "https://eve.gd/2012/01/06/adorno-terminology-άλλο-γένος/")]
        mapping, _ = build_mapping(posts, eprints)
        self.assertEqual(
            mapping[posts[0]["file"]],
            "https://eprints.bbk.ac.uk/id/eprint/17386/",
        )

    def test_mixed_greek_and_ascii_with_three_byte_char(self):
        # χωρισμός contains ό (U+1F79), a three-byte UTF-8 sequence
        # (e1 bd b9), followed by a plain-ASCII gloss in the slug.
        posts = [
            post(
                "2012-01-06-adorno-terminology-cf-87-cf-89-cf-81-ce-b9-cf-83-"
                "ce-bc-e1-bd-b9-cf-82-chorismos.md"
            )
        ]
        eprints = [
            eprint(
                17387,
                "https://eve.gd/2012/01/06/adorno-terminology-"
                "%25cf%2587%25cf%2589%25cf%2581%25ce%25b9%25cf%2583"
                "%25ce%25bc%25e1%25bd%25b9%25cf%2582-chorismos/",
            )
        ]
        mapping, _ = build_mapping(posts, eprints)
        self.assertEqual(
            mapping[posts[0]["file"]],
            "https://eprints.bbk.ac.uk/id/eprint/17387/",
        )

    def test_unrelated_greek_posts_do_not_cross_match(self):
        posts = [
            post("2012-01-06-adorno-terminology-ce-ac-ce-bb-ce-bb-ce-bf-ce-b3-ce-ad-ce-bd-ce-bf-cf-82.md"),
            post("2012-01-07-adorno-terminology-ce-b8-ce-ad-cf-83-ce-b5-ce-b9.md"),
        ]
        eprints = [
            eprint(
                17386,
                "https://eve.gd/2012/01/06/adorno-terminology-"
                "%25ce%25ac%25ce%25bb%25ce%25bb%25ce%25bf-"
                "%25ce%25b3%25ce%25ad%25ce%25bd%25ce%25bf%25cf%2582/",
            )
        ]
        mapping, _ = build_mapping(posts, eprints)
        self.assertEqual(
            mapping[posts[0]["file"]],
            "https://eprints.bbk.ac.uk/id/eprint/17386/",
        )
        self.assertIsNone(mapping[posts[1]["file"]])


if __name__ == "__main__":
    unittest.main()
