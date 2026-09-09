"""Behavioural tests for the BIROn apply script (run from the blog root):

    uv run --with pyyaml --with pytest -m pytest _tests/test_apply_biron.py
"""

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_biron"))

import apply_biron


BIRON_URL = "https://eprints.bbk.ac.uk/id/eprint/57592/"

FM_WITH_KCWORKS = """---
title: "A post"
layout: post
date: 2026-08-28
doi: https://doi.org/10.59348/mjvdw-w0051
roguescholar: https://rogue-scholar.org/records/26jfx-f4w16
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mufm2bxodp24
kcworks: https://works.hcommons.org/records/83n59-ana25
image:
  feature: metadatatiles.jpg
---

Body text mentioning doi: https://doi.org/10.1000/example inline.
"""

FM_WITHOUT_KCWORKS = """---
title: "An older post"
layout: post
date: 2007-05-15
doi: https://doi.org/10.59348/2zhsq-kgd29
atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mntm2c32p
comments: []
---

Old body.
"""

FM_DOI_ONLY = """---
title: "A plain post"
layout: post
doi: https://doi.org/10.59348/2zhsq-kgd29
---

Body.
"""

FM_BARE = """---
title: "A page"
layout: post
---

Body.
"""


# --- insert_biron ----------------------------------------------------------


def test_inserts_after_kcworks_line():
    out = apply_biron.insert_biron(FM_WITH_KCWORKS, biron=BIRON_URL)
    lines = out.splitlines()
    kc = lines.index("kcworks: https://works.hcommons.org/records/83n59-ana25")
    assert lines[kc + 1] == f"biron: {BIRON_URL}"


def test_inserts_after_atproto_when_no_kcworks():
    out = apply_biron.insert_biron(FM_WITHOUT_KCWORKS, biron=BIRON_URL)
    lines = out.splitlines()
    at = lines.index(
        "atproto: at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mq7mntm2c32p"
    )
    assert lines[at + 1] == f"biron: {BIRON_URL}"


def test_inserts_after_doi_when_no_other_anchor():
    out = apply_biron.insert_biron(FM_DOI_ONLY, biron=BIRON_URL)
    lines = out.splitlines()
    doi = lines.index("doi: https://doi.org/10.59348/2zhsq-kgd29")
    assert lines[doi + 1] == f"biron: {BIRON_URL}"


def test_appends_at_end_of_front_matter_without_anchors():
    out = apply_biron.insert_biron(FM_BARE, biron=BIRON_URL)
    lines = out.splitlines()
    close = lines.index("---", 1)
    assert lines[close - 1] == f"biron: {BIRON_URL}"


def test_replaces_existing_biron_line_idempotently():
    once = apply_biron.insert_biron(FM_WITH_KCWORKS, biron=BIRON_URL)
    twice = apply_biron.insert_biron(once, biron=BIRON_URL)
    assert twice == once
    other = apply_biron.insert_biron(once, biron="https://eprints.bbk.ac.uk/id/eprint/1/")
    assert other.count("biron:") == 1
    assert "biron: https://eprints.bbk.ac.uk/id/eprint/1/" in other


def test_none_removes_existing_biron_line():
    once = apply_biron.insert_biron(FM_WITH_KCWORKS, biron=BIRON_URL)
    out = apply_biron.insert_biron(once, biron=None)
    assert "biron:" not in out


def test_body_and_other_front_matter_unchanged():
    out = apply_biron.insert_biron(FM_WITH_KCWORKS, biron=BIRON_URL)
    assert "Body text mentioning doi: https://doi.org/10.1000/example inline." in out
    assert 'title: "A post"' in out
    assert "  feature: metadatatiles.jpg" in out


def test_refuses_crlf():
    with pytest.raises(ValueError):
        apply_biron.insert_biron(FM_BARE.replace("\n", "\r\n"), biron=BIRON_URL)


def test_refuses_missing_front_matter():
    with pytest.raises(ValueError):
        apply_biron.insert_biron("No front matter here.\n", biron=BIRON_URL)


# --- build_mapping ---------------------------------------------------------


def _eprint(eprintid, url=None, doi=None, title=None):
    return {
        "eprintid": eprintid,
        "uri": f"https://eprints.bbk.ac.uk/id/eprint/{eprintid}",
        "url": url,
        "doi": doi,
        "title": title,
    }


def _post(fname, doi=None):
    year, month, day, slug = fname[:-3].split("-", 3)
    return {"file": fname, "doi": doi, "path": f"/{year}/{month}/{day}/{slug}"}


def test_matches_by_official_url_path():
    posts = [_post("2026-06-23-making-blog-posts-harvestable.md")]
    eprints = [_eprint(57592, url="https://eve.gd/2026/06/23/making-blog-posts-harvestable/")]
    mapping, anomalies = apply_biron.build_mapping(posts, eprints)
    assert mapping == {
        "2026-06-23-making-blog-posts-harvestable.md": "https://eprints.bbk.ac.uk/id/eprint/57592/"
    }
    assert anomalies == []


def test_url_match_ignores_scheme_and_trailing_slash():
    posts = [_post("2015-01-02-some-post.md")]
    eprints = [_eprint(100, url="http://eve.gd/2015/01/02/some-post")]
    mapping, _ = apply_biron.build_mapping(posts, eprints)
    assert mapping["2015-01-02-some-post.md"] == "https://eprints.bbk.ac.uk/id/eprint/100/"


def test_unmatched_post_maps_to_none():
    posts = [_post("2015-01-02-some-post.md")]
    mapping, anomalies = apply_biron.build_mapping(posts, [])
    assert mapping == {"2015-01-02-some-post.md": None}
    assert any("2015-01-02-some-post.md" in a for a in anomalies)


def test_doi_match_when_url_differs_but_slug_agrees():
    # Date drift between the blog and the deposit: DOI + slug agreement wins.
    posts = [_post("2020-03-04-drifted-post.md", doi="https://doi.org/10.59348/abc12-def34")]
    eprints = [
        _eprint(200, url="https://eve.gd/2020/03/05/drifted-post/", doi="10.59348/abc12-def34")
    ]
    mapping, _ = apply_biron.build_mapping(posts, eprints)
    assert mapping["2020-03-04-drifted-post.md"] == "https://eprints.bbk.ac.uk/id/eprint/200/"


def test_doi_match_rejected_on_slug_mismatch():
    # A copy-pasted DOI pointing at a different post must not create a link.
    posts = [_post("2020-03-04-original-post.md", doi="https://doi.org/10.59348/abc12-def34")]
    eprints = [
        _eprint(200, url="https://eve.gd/2019/01/01/other-post/", doi="10.59348/abc12-def34")
    ]
    mapping, anomalies = apply_biron.build_mapping(posts, eprints)
    assert mapping["2020-03-04-original-post.md"] is None
    assert any("slug mismatch" in a for a in anomalies)


def test_duplicate_official_url_prefers_oldest_eprint():
    posts = [_post("2015-01-02-some-post.md")]
    eprints = [
        _eprint(300, url="https://eve.gd/2015/01/02/some-post/"),
        _eprint(150, url="https://eve.gd/2015/01/02/some-post/"),
    ]
    mapping, anomalies = apply_biron.build_mapping(posts, eprints)
    assert mapping["2015-01-02-some-post.md"] == "https://eprints.bbk.ac.uk/id/eprint/150/"
    assert any("duplicate" in a.lower() for a in anomalies)


def test_slug_fallback_when_dates_drift_and_no_doi():
    posts = [_post("2020-03-04-drifted-post.md")]
    eprints = [_eprint(400, url="https://eve.gd/2020/03/05/drifted-post/")]
    mapping, anomalies = apply_biron.build_mapping(posts, eprints)
    assert mapping["2020-03-04-drifted-post.md"] == "https://eprints.bbk.ac.uk/id/eprint/400/"
    assert any("drift" in a.lower() or "slug" in a.lower() for a in anomalies)


def test_slug_fallback_refused_when_ambiguous():
    posts = [_post("2020-03-04-drifted-post.md")]
    eprints = [
        _eprint(400, url="https://eve.gd/2020/03/05/drifted-post/"),
        _eprint(401, url="https://eve.gd/2021/07/08/drifted-post/"),
    ]
    mapping, _ = apply_biron.build_mapping(posts, eprints)
    assert mapping["2020-03-04-drifted-post.md"] is None


def test_eprint_not_claimed_by_two_posts_via_slug_fallback():
    # Two posts sharing a slug must not both grab the same eprint.
    posts = [_post("2020-03-04-drifted-post.md"), _post("2021-05-06-drifted-post.md")]
    eprints = [_eprint(400, url="https://eve.gd/2020/03/05/drifted-post/")]
    mapping, _ = apply_biron.build_mapping(posts, eprints)
    assert list(mapping.values()).count("https://eprints.bbk.ac.uk/id/eprint/400/") <= 1


def test_percent_encoded_urls_match():
    posts = [_post("2015-01-02-café-post.md")]
    eprints = [_eprint(500, url="https://eve.gd/2015/01/02/caf%C3%A9-post/")]
    mapping, _ = apply_biron.build_mapping(posts, eprints)
    assert mapping["2015-01-02-café-post.md"] == "https://eprints.bbk.ac.uk/id/eprint/500/"


def test_double_encoded_greek_url_matches_dashed_hex_slug():
    # BIROn official_urls are sometimes double percent-encoded (%25ce%25ac…),
    # while the blog's slugifier spelled Greek titles as dashed hex UTF-8
    # bytes with the word-separator hyphens collapsed.
    posts = [
        _post("2012-01-06-adorno-terminology-ce-ac-ce-bb-ce-bb-ce-bf-ce-b3-ce-ad-ce-bd-ce-bf-cf-82.md")
    ]
    eprints = [
        _eprint(
            17386,
            url="https://eve.gd/2012/01/06/adorno-terminology-"
            "%25ce%25ac%25ce%25bb%25ce%25bb%25ce%25bf-"
            "%25ce%25b3%25ce%25ad%25ce%25bd%25ce%25bf%25cf%2582/",
            title="Adorno terminology: άλλο γένος",
        )
    ]
    mapping, anomalies = apply_biron.build_mapping(posts, eprints)
    assert mapping[posts[0]["file"]] == "https://eprints.bbk.ac.uk/id/eprint/17386/"
    assert anomalies == []


def test_literal_greek_url_matches_dashed_hex_slug():
    posts = [
        _post("2012-01-06-adorno-terminology-ce-ac-ce-bb-ce-bb-ce-bf-ce-b3-ce-ad-ce-bd-ce-bf-cf-82.md")
    ]
    eprints = [_eprint(17386, url="https://eve.gd/2012/01/06/adorno-terminology-άλλο-γένος/")]
    mapping, _ = apply_biron.build_mapping(posts, eprints)
    assert mapping[posts[0]["file"]] == "https://eprints.bbk.ac.uk/id/eprint/17386/"


def test_mixed_greek_and_ascii_with_three_byte_char():
    # χωρισμός contains ό (U+1F79), a three-byte UTF-8 sequence (e1 bd b9),
    # followed by a plain-ASCII gloss in the slug.
    posts = [
        _post(
            "2012-01-06-adorno-terminology-cf-87-cf-89-cf-81-ce-b9-cf-83-"
            "ce-bc-e1-bd-b9-cf-82-chorismos.md"
        )
    ]
    eprints = [
        _eprint(
            17038,
            url="https://eve.gd/2012/01/06/adorno-terminology-"
            "%25cf%2587%25cf%2589%25cf%2581%25ce%25b9%25cf%2583"
            "%25ce%25bc%25e1%25bd%25b9%25cf%2582-chorismos/",
        )
    ]
    mapping, _ = apply_biron.build_mapping(posts, eprints)
    assert mapping[posts[0]["file"]] == "https://eprints.bbk.ac.uk/id/eprint/17038/"


def test_unrelated_greek_posts_do_not_cross_match():
    posts = [
        _post("2012-01-06-adorno-terminology-ce-ac-ce-bb-ce-bb-ce-bf-ce-b3-ce-ad-ce-bd-ce-bf-cf-82.md"),
        _post("2012-01-07-adorno-terminology-ce-b8-ce-ad-cf-83-ce-b5-ce-b9.md"),
    ]
    eprints = [
        _eprint(
            17386,
            url="https://eve.gd/2012/01/06/adorno-terminology-"
            "%25ce%25ac%25ce%25bb%25ce%25bb%25ce%25bf-"
            "%25ce%25b3%25ce%25ad%25ce%25bd%25ce%25bf%25cf%2582/",
        )
    ]
    mapping, _ = apply_biron.build_mapping(posts, eprints)
    assert mapping[posts[0]["file"]] == "https://eprints.bbk.ac.uk/id/eprint/17386/"
    assert mapping[posts[1]["file"]] is None


def test_url_fragment_ignored():
    posts = [_post("2025-01-08-getting-kc-works-running-locally.md")]
    eprints = [
        _eprint(600, url="https://eve.gd/2025/01/08/getting-kc-works-running-locally/#fn:1")
    ]
    mapping, _ = apply_biron.build_mapping(posts, eprints)
    assert mapping["2025-01-08-getting-kc-works-running-locally.md"] == (
        "https://eprints.bbk.ac.uk/id/eprint/600/"
    )


# --- unclaimed_blog_eprints ------------------------------------------------


def test_unclaimed_lists_blog_deposits_no_post_took():
    eprints = [
        _eprint(100, url="https://eve.gd/2015/01/02/some-post/"),
        _eprint(200, url="https://eve.gd/2016/01/02/other-post/"),
        _eprint(300, doi="10.1234/journal-article"),
        dict(_eprint(400), publication="eve.gd"),
    ]
    mapping = {"2015-01-02-some-post.md": "https://eprints.bbk.ac.uk/id/eprint/100/"}
    out = apply_biron.unclaimed_blog_eprints(mapping, eprints)
    assert [e["eprintid"] for e in out] == [200, 400]


def test_unclaimed_empty_when_everything_matched():
    eprints = [_eprint(100, url="https://eve.gd/2015/01/02/some-post/")]
    mapping = {"2015-01-02-some-post.md": "https://eprints.bbk.ac.uk/id/eprint/100/"}
    assert apply_biron.unclaimed_blog_eprints(mapping, eprints) == []


# --- apply_overrides -------------------------------------------------------


def test_overrides_fill_unmatched_posts():
    mapping = {"2023-07-28-rules-vs-principles-in-posi.md": None}
    eprints = [_eprint(52882)]
    out = apply_biron.apply_overrides(
        mapping, {"2023-07-28-rules-vs-principles-in-posi.md": 52882}, eprints
    )
    assert out["2023-07-28-rules-vs-principles-in-posi.md"] == (
        "https://eprints.bbk.ac.uk/id/eprint/52882/"
    )


def test_override_for_unknown_eprint_raises():
    with pytest.raises(ValueError):
        apply_biron.apply_overrides({"a.md": None}, {"a.md": 999999}, [])
