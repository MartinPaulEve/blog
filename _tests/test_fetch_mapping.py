"""Behavioural tests for the BIROn fetch/report script (run from the blog root):

    uv run --with pyyaml --with pytest -m pytest _tests/test_fetch_mapping.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_biron"))

import fetch_mapping


def test_render_anomalies_covers_all_review_material():
    anomalies = [
        "duplicate official_url /2016/12/06/five on eprints [17578, 17598]; keeping 17578",
        "2015-01-02-unmatched-post.md: no BIROn eprint found",
    ]
    mapping = {
        "2015-01-02-unmatched-post.md": None,
        "2015-01-03-matched-post.md": "https://eprints.bbk.ac.uk/id/eprint/100/",
    }
    titles = {
        "2015-01-02-unmatched-post.md": "An Unmatched Post",
        "2015-01-03-matched-post.md": "A Matched Post",
    }
    unclaimed = [
        {
            "eprintid": 26049,
            "uri": "https://eprints.bbk.ac.uk/id/eprint/26049",
            "official_url": "http://meve.io/talk",
            "title": "A Stray Deposit",
        }
    ]
    out = fetch_mapping.render_anomalies(anomalies, mapping, titles, unclaimed)

    # every unmatched post appears, with its title
    assert "2015-01-02-unmatched-post.md" in out
    assert "An Unmatched Post" in out
    # matched posts do not clutter the review file
    assert "2015-01-03-matched-post.md" not in out
    # every unclaimed eprint appears, with id, title, and deposit URL
    assert "26049" in out
    assert "A Stray Deposit" in out
    assert "http://meve.io/talk" in out
    # matching notes survive; the raw "no eprint" lines are subsumed by
    # the unmatched-posts section rather than duplicated
    assert "duplicate official_url" in out
    assert "no BIROn eprint found" not in out


def test_render_anomalies_handles_missing_titles_and_urls():
    mapping = {"2015-01-02-unmatched-post.md": None}
    unclaimed = [
        {
            "eprintid": 400,
            "uri": "https://eprints.bbk.ac.uk/id/eprint/400",
            "official_url": None,
            "title": None,
        }
    ]
    out = fetch_mapping.render_anomalies([], mapping, {}, unclaimed)
    assert "2015-01-02-unmatched-post.md" in out
    assert "400" in out
