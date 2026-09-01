"""Behavioural tests for the identifier apply script (run from the blog root):

    uv run --with pyyaml --with pytest -m pytest _tests/test_apply_identifiers.py
"""

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_identifiers"))

import apply_identifiers


RS_URL = "https://rogue-scholar.org/records/26jfx-f4w16"
AT_URI = "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3mufm2bxodp24"

FM_WITH_KCWORKS = """---
title: "A post"
layout: post
date: 2026-08-28
doi: https://doi.org/10.59348/mjvdw-w0051
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
comments: []
---

Old body.
"""

FM_NO_DOI = """---
title: "A page"
layout: post
---

Body.
"""


# --- insert_identifiers ----------------------------------------------------


def test_inserts_both_keys_after_kcworks_line():
    out = apply_identifiers.insert_identifiers(
        FM_WITH_KCWORKS, roguescholar=RS_URL, atproto=AT_URI
    )
    lines = out.splitlines()
    kc = lines.index("kcworks: https://works.hcommons.org/records/83n59-ana25")
    assert lines[kc + 1] == f"roguescholar: {RS_URL}"
    assert lines[kc + 2] == f"atproto: {AT_URI}"


def test_inserts_after_doi_line_when_no_kcworks():
    out = apply_identifiers.insert_identifiers(
        FM_WITHOUT_KCWORKS, roguescholar=RS_URL, atproto=AT_URI
    )
    lines = out.splitlines()
    doi = lines.index("doi: https://doi.org/10.59348/2zhsq-kgd29")
    assert lines[doi + 1] == f"roguescholar: {RS_URL}"
    assert lines[doi + 2] == f"atproto: {AT_URI}"


def test_body_and_other_front_matter_unchanged():
    out = apply_identifiers.insert_identifiers(
        FM_WITH_KCWORKS, roguescholar=RS_URL, atproto=AT_URI
    )
    assert "Body text mentioning doi: https://doi.org/10.1000/example inline." in out
    assert 'title: "A post"' in out
    assert "image:\n  feature: metadatatiles.jpg" in out
    # the body's inline "doi:" must not attract an insertion
    assert out.count("roguescholar:") == 1
    assert out.count("atproto:") == 1


def test_atproto_only_when_no_roguescholar_match():
    out = apply_identifiers.insert_identifiers(FM_WITH_KCWORKS, atproto=AT_URI)
    assert "roguescholar:" not in out
    lines = out.splitlines()
    kc = lines.index("kcworks: https://works.hcommons.org/records/83n59-ana25")
    assert lines[kc + 1] == f"atproto: {AT_URI}"


def test_replaces_existing_values_idempotently():
    once = apply_identifiers.insert_identifiers(
        FM_WITH_KCWORKS, roguescholar=RS_URL, atproto=AT_URI
    )
    twice = apply_identifiers.insert_identifiers(
        once, roguescholar=RS_URL, atproto=AT_URI
    )
    assert once == twice
    updated = apply_identifiers.insert_identifiers(
        once,
        roguescholar="https://rogue-scholar.org/records/other-id123",
        atproto=AT_URI,
    )
    assert "roguescholar: https://rogue-scholar.org/records/other-id123" in updated
    assert updated.count("roguescholar:") == 1


def test_appends_to_front_matter_when_no_doi_or_kcworks():
    out = apply_identifiers.insert_identifiers(FM_NO_DOI, atproto=AT_URI)
    fm = out.split("---\n")[1]
    assert f"atproto: {AT_URI}\n" in fm
    assert "Body." in out


def test_rejects_text_without_front_matter():
    with pytest.raises(ValueError):
        apply_identifiers.insert_identifiers("no front matter here", atproto=AT_URI)


def test_rejects_crlf_line_endings():
    with pytest.raises(ValueError):
        apply_identifiers.insert_identifiers(
            FM_WITH_KCWORKS.replace("\n", "\r\n"), atproto=AT_URI
        )


# --- build_mapping ---------------------------------------------------------


def _records():
    return [
        {
            "id": "aaaaa-11111",
            "doi": "10.59348/aaaaa-doi01",
            "url": "https://eve.gd/2020/01/01/first-post/",
            "created": "2024-01-01T00:00:00+00:00",
        },
        {
            "id": "bbbbb-22222",
            "doi": "10.59348/bbbbb-doi02",
            "url": "https://eve.gd/2021/02/02/second-post/",
            "created": "2024-01-01T00:00:00+00:00",
        },
        # duplicate pair for the same URL: an older and a newer harvest
        {
            "id": "ccccc-33333",
            "doi": "10.59348/ccccc-doi03",
            "url": "https://eve.gd/2015/03/05/third-post",
            "created": "2024-10-20T08:59:06+00:00",
        },
        {
            "id": "ddddd-44444",
            "doi": "10.59348/ddddd-doi04",
            "url": "https://eve.gd/2015/03/05/third-post/",
            "created": "2025-09-30T00:32:43+00:00",
        },
        # percent-encoded URL
        {
            "id": "eeeee-55555",
            "doi": "10.59348/eeeee-doi05",
            "url": "https://eve.gd/2021/08/19/thomas-pynchon-from-s-ger%C3%A4t-to-y-ger%C3%A4t/",
            "created": "2024-01-01T00:00:00+00:00",
        },
    ]


def _atdocs():
    return [
        {"uri": "at://did:plc:x/site.standard.document/rkey1", "path": "/2020/01/01/first-post"},
        {"uri": "at://did:plc:x/site.standard.document/rkey2", "path": "/2021/02/02/second-post"},
        {"uri": "at://did:plc:x/site.standard.document/rkey3", "path": "/2015/03/05/third-post"},
        {"uri": "at://did:plc:x/site.standard.document/rkey5", "path": "/2021/08/19/thomas-pynchon-from-s-gerät-to-y-gerät"},
    ]


def test_matches_by_doi_and_by_path():
    posts = [
        {"file": "2020-01-01-first-post.md", "doi": "https://doi.org/10.59348/aaaaa-doi01", "path": "/2020/01/01/first-post"},
        {"file": "2021-02-02-second-post.md", "doi": None, "path": "/2021/02/02/second-post"},
    ]
    mapping, _anomalies = apply_identifiers.build_mapping(posts, _records(), _atdocs())
    assert mapping["2020-01-01-first-post.md"]["roguescholar"] == "https://rogue-scholar.org/records/aaaaa-11111"
    assert mapping["2020-01-01-first-post.md"]["atproto"] == "at://did:plc:x/site.standard.document/rkey1"
    # DOI missing -> falls back to URL path match
    assert mapping["2021-02-02-second-post.md"]["roguescholar"] == "https://rogue-scholar.org/records/bbbbb-22222"


def test_url_fallback_prefers_oldest_record_for_duplicate_urls():
    posts = [
        {"file": "2015-03-05-third-post.md", "doi": "10.1629/uksg.166", "path": "/2015/03/05/third-post"},
    ]
    mapping, _anomalies = apply_identifiers.build_mapping(posts, _records(), _atdocs())
    assert mapping["2015-03-05-third-post.md"]["roguescholar"] == "https://rogue-scholar.org/records/ccccc-33333"


def test_percent_encoded_urls_match_unicode_paths():
    posts = [
        {"file": "2021-08-19-thomas.md", "doi": None, "path": "/2021/08/19/thomas-pynchon-from-s-gerät-to-y-gerät"},
    ]
    mapping, _anomalies = apply_identifiers.build_mapping(posts, _records(), _atdocs())
    assert mapping["2021-08-19-thomas.md"]["roguescholar"] == "https://rogue-scholar.org/records/eeeee-55555"
    assert mapping["2021-08-19-thomas.md"]["atproto"] == "at://did:plc:x/site.standard.document/rkey5"


def test_unmatched_post_flagged_and_gets_no_roguescholar():
    posts = [
        {"file": "2025-10-04-pangolin.md", "doi": "https://doi.org/10.59348/bbbbb-doi02", "path": "/2025/10/04/pangolin"},
    ]
    mapping, anomalies = apply_identifiers.build_mapping(posts, _records(), _atdocs())
    # DOI resolves to a record whose URL belongs to a different path: suspect,
    # and there is no URL match either -> no roguescholar value.
    assert mapping["2025-10-04-pangolin.md"]["roguescholar"] is None
    assert any("2025-10-04-pangolin.md" in a for a in anomalies)


def test_two_posts_claiming_same_record_flagged():
    posts = [
        {"file": "2021-02-02-second-post.md", "doi": "10.59348/bbbbb-doi02", "path": "/2021/02/02/second-post"},
        {"file": "2025-10-04-pangolin.md", "doi": "10.59348/bbbbb-doi02", "path": "/2025/10/04/pangolin"},
    ]
    mapping, anomalies = apply_identifiers.build_mapping(posts, _records(), _atdocs())
    assert mapping["2021-02-02-second-post.md"]["roguescholar"] == "https://rogue-scholar.org/records/bbbbb-22222"
    assert mapping["2025-10-04-pangolin.md"]["roguescholar"] is None
    assert any("pangolin" in a for a in anomalies)


def test_post_without_atproto_doc_flagged():
    posts = [
        {"file": "2020-01-01-first-post.md", "doi": "10.59348/aaaaa-doi01", "path": "/2020/01/01/first-post"},
        {"file": "2099-01-01-future.md", "doi": None, "path": "/2099/01/01/future"},
    ]
    mapping, anomalies = apply_identifiers.build_mapping(posts, _records(), _atdocs())
    assert mapping["2099-01-01-future.md"]["atproto"] is None
    assert any("2099-01-01-future.md" in a for a in anomalies)
