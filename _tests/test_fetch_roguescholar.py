"""Behavioural tests for the Rogue Scholar fetch tool (run from the blog root):

    uv run --with pyyaml --with pytest -m pytest _tests/test_fetch_roguescholar.py
"""

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_identifiers"))

import fetch_roguescholar


RS_URL = "https://rogue-scholar.org/records/e9nww-03n64"
AT_URI = "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3muryvfaafi24"

POST_WITH_ATURI_ONLY = """---
title: "A post"
layout: post
date: 2026-09-05
doi: https://doi.org/10.59348/6fdyv-pjk84
kcworks: https://works.hcommons.org/records/3deyv-nm119
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3muryvfaafi24"
---
Body text.
"""

POST_WITH_ATPROTO = """---
title: "A post"
layout: post
date: 2026-09-05
doi: https://doi.org/10.59348/6fdyv-pjk84
kcworks: https://works.hcommons.org/records/3deyv-nm119
atproto: at://did:plc:example/site.standard.document/existing123
atUri: "at://did:plc:hnpt7ns2lecdujegbi6qkqqm/site.standard.document/3muryvfaafi24"
---
Body text.
"""


class TestStampRoguescholar:
    def test_adds_roguescholar_after_kcworks(self):
        result = fetch_roguescholar.stamp_roguescholar(
            POST_WITH_ATURI_ONLY, RS_URL
        )
        assert (
            "kcworks: https://works.hcommons.org/records/3deyv-nm119\n"
            f"roguescholar: {RS_URL}\n"
        ) in result

    def test_mirrors_aturi_into_atproto_when_missing(self):
        result = fetch_roguescholar.stamp_roguescholar(
            POST_WITH_ATURI_ONLY, RS_URL
        )
        assert f"\natproto: {AT_URI}\n" in result
        # the original quoted atUri line is untouched
        assert f'atUri: "{AT_URI}"' in result

    def test_preserves_existing_atproto_value(self):
        result = fetch_roguescholar.stamp_roguescholar(
            POST_WITH_ATPROTO, RS_URL
        )
        assert (
            "atproto: at://did:plc:example/site.standard.document/existing123"
            in result
        )
        assert result.count("atproto:") == 1

    def test_is_idempotent(self):
        once = fetch_roguescholar.stamp_roguescholar(
            POST_WITH_ATURI_ONLY, RS_URL
        )
        twice = fetch_roguescholar.stamp_roguescholar(once, RS_URL)
        assert once == twice

    def test_body_is_untouched(self):
        result = fetch_roguescholar.stamp_roguescholar(
            POST_WITH_ATURI_ONLY, RS_URL
        )
        assert result.endswith("---\nBody text.\n")

    def test_no_front_matter_raises(self):
        with pytest.raises(ValueError):
            fetch_roguescholar.stamp_roguescholar("Plain file.\n", RS_URL)


class TestFindRecordUrl:
    POST = {
        "file": "2026-09-05-a-post.md",
        "doi": "https://doi.org/10.59348/6fdyv-pjk84",
        "path": "/2026/09/05/a-post",
    }

    def test_matches_by_doi(self):
        records = [
            {
                "id": "e9nww-03n64",
                "doi": "10.59348/6fdyv-pjk84",
                "url": "https://eve.gd/2026/09/05/a-post/",
                "created": "2026-09-05T10:00:00",
            }
        ]
        url, _ = fetch_roguescholar.find_record_url(self.POST, records)
        assert url == RS_URL

    def test_falls_back_to_url_path_match(self):
        records = [
            {
                "id": "e9nww-03n64",
                "doi": None,
                "url": "https://eve.gd/2026/09/05/a-post/",
                "created": "2026-09-05T10:00:00",
            }
        ]
        url, _ = fetch_roguescholar.find_record_url(self.POST, records)
        assert url == RS_URL

    def test_returns_none_when_not_yet_harvested(self):
        records = [
            {
                "id": "other-rec",
                "doi": "10.59348/other",
                "url": "https://eve.gd/2026/01/01/another-post/",
                "created": "2026-01-01T10:00:00",
            }
        ]
        url, _ = fetch_roguescholar.find_record_url(self.POST, records)
        assert url is None

    def test_atproto_anomalies_are_not_reported(self):
        # find_record_url borrows build_mapping, which flags missing
        # atProto documents; that is noise for a Rogue Scholar lookup.
        url, anomalies = fetch_roguescholar.find_record_url(self.POST, [])
        assert url is None
        assert not any("atProto" in a for a in anomalies)


class TestLoadPost:
    def test_reads_doi_and_derives_permalink_path(self, tmp_path):
        post = tmp_path / "2026-09-05-a-post.md"
        post.write_text(POST_WITH_ATURI_ONLY, encoding="utf-8")
        loaded = fetch_roguescholar.load_post(str(post))
        assert loaded == {
            "file": "2026-09-05-a-post.md",
            "doi": "https://doi.org/10.59348/6fdyv-pjk84",
            "path": "/2026/09/05/a-post",
        }

    def test_post_without_front_matter_raises(self, tmp_path):
        post = tmp_path / "2026-09-05-b-post.md"
        post.write_text("Plain file.\n", encoding="utf-8")
        with pytest.raises(ValueError):
            fetch_roguescholar.load_post(str(post))
