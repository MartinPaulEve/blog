"""Behavioural tests for the human.json manager (run from the blog root):

    uv run --with pytest -m pytest _tests/test_human_json.py
"""

import datetime
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_human"))

import human_json as hj


def make_data(*vouches):
    return {
        "version": hj.SPEC_VERSION,
        "url": hj.SITE_URL,
        "vouches": [{"url": u, "vouched_at": d} for u, d in vouches],
    }


class TestCanonicalUrl:
    def test_bare_domain_becomes_https_url(self):
        assert hj.canonical_url("kfitz.info") == "https://kfitz.info"

    def test_existing_https_url_is_preserved(self):
        assert hj.canonical_url("https://brennan.day") == "https://brennan.day"

    def test_trailing_slash_is_stripped(self):
        assert hj.canonical_url("https://kfitz.info/") == "https://kfitz.info"

    def test_host_is_lowercased(self):
        assert hj.canonical_url("KFitz.INFO") == "https://kfitz.info"

    def test_path_is_kept_for_sites_under_a_prefix(self):
        assert (
            hj.canonical_url("example.com/~alice")
            == "https://example.com/~alice"
        )

    def test_path_case_is_preserved(self):
        assert (
            hj.canonical_url("Example.com/~Alice")
            == "https://example.com/~Alice"
        )

    def test_explicit_http_scheme_is_preserved(self):
        assert hj.canonical_url("http://old.example") == "http://old.example"


class TestLoad:
    def test_missing_file_yields_skeleton(self, tmp_path):
        data = hj.load(tmp_path / "human.json")
        assert data == {
            "version": hj.SPEC_VERSION,
            "url": hj.SITE_URL,
            "vouches": [],
        }

    def test_existing_file_is_read(self, tmp_path):
        path = tmp_path / "human.json"
        expected = make_data(("https://kfitz.info", "2026-09-03"))
        path.write_text(json.dumps(expected))
        assert hj.load(path) == expected


class TestSave:
    def test_round_trips_through_load(self, tmp_path):
        path = tmp_path / "human.json"
        data = make_data(("https://kfitz.info", "2026-09-03"))
        hj.save(data, path)
        assert hj.load(path) == data

    def test_output_is_pretty_printed_with_final_newline(self, tmp_path):
        path = tmp_path / "human.json"
        hj.save(make_data(("https://kfitz.info", "2026-09-03")), path)
        text = path.read_text()
        assert text.endswith("\n")
        assert "\n  " in text  # indented, not a single line


class TestAddVouch:
    def test_adds_a_canonicalized_vouch(self):
        data = make_data()
        assert hj.add_vouch(data, "kfitz.info", "2026-09-03") is True
        assert data["vouches"] == [
            {"url": "https://kfitz.info", "vouched_at": "2026-09-03"}
        ]

    def test_duplicate_is_rejected_and_unchanged(self):
        data = make_data(("https://kfitz.info", "2026-01-01"))
        assert hj.add_vouch(data, "kfitz.info", "2026-09-03") is False
        assert data["vouches"] == [
            {"url": "https://kfitz.info", "vouched_at": "2026-01-01"}
        ]

    def test_duplicate_detection_ignores_case_and_trailing_slash(self):
        data = make_data(("https://kfitz.info", "2026-01-01"))
        assert hj.add_vouch(data, "KFITZ.info/", "2026-09-03") is False
        assert len(data["vouches"]) == 1

    def test_appends_after_existing_vouches(self):
        data = make_data(("https://kfitz.info", "2026-01-01"))
        hj.add_vouch(data, "brennan.day", "2026-09-03")
        assert [v["url"] for v in data["vouches"]] == [
            "https://kfitz.info",
            "https://brennan.day",
        ]


class TestRevokeVouch:
    def test_removes_the_vouch(self):
        data = make_data(
            ("https://kfitz.info", "2026-01-01"),
            ("https://brennan.day", "2026-01-02"),
        )
        assert hj.revoke_vouch(data, "kfitz.info") is True
        assert [v["url"] for v in data["vouches"]] == ["https://brennan.day"]

    def test_unknown_site_is_reported_and_nothing_changes(self):
        data = make_data(("https://kfitz.info", "2026-01-01"))
        assert hj.revoke_vouch(data, "unknown.example") is False
        assert len(data["vouches"]) == 1

    def test_matches_ignore_case_and_trailing_slash(self):
        data = make_data(("https://kfitz.info", "2026-01-01"))
        assert hj.revoke_vouch(data, "https://KFITZ.INFO/") is True
        assert data["vouches"] == []


class TestRenewVouch:
    def test_updates_the_date_in_place(self):
        data = make_data(
            ("https://kfitz.info", "2026-01-01"),
            ("https://brennan.day", "2026-01-02"),
        )
        assert hj.renew_vouch(data, "kfitz.info", "2026-09-03") is True
        assert data["vouches"] == [
            {"url": "https://kfitz.info", "vouched_at": "2026-09-03"},
            {"url": "https://brennan.day", "vouched_at": "2026-01-02"},
        ]

    def test_unknown_site_is_reported_and_nothing_changes(self):
        data = make_data(("https://kfitz.info", "2026-01-01"))
        assert hj.renew_vouch(data, "unknown.example", "2026-09-03") is False
        assert data["vouches"][0]["vouched_at"] == "2026-01-01"


class TestMain:
    def test_add_writes_the_vouch_and_exits_zero(self, tmp_path):
        path = tmp_path / "human.json"
        code = hj.main(
            ["add", "kfitz.info", "--file", str(path), "--date", "2026-09-03"]
        )
        assert code == 0
        assert hj.load(path)["vouches"] == [
            {"url": "https://kfitz.info", "vouched_at": "2026-09-03"}
        ]

    def test_add_duplicate_exits_nonzero_and_preserves_file(self, tmp_path):
        path = tmp_path / "human.json"
        hj.save(make_data(("https://kfitz.info", "2026-01-01")), path)
        code = hj.main(
            ["add", "kfitz.info", "--file", str(path), "--date", "2026-09-03"]
        )
        assert code != 0
        assert hj.load(path)["vouches"][0]["vouched_at"] == "2026-01-01"

    def test_revoke_removes_and_exits_zero(self, tmp_path):
        path = tmp_path / "human.json"
        hj.save(make_data(("https://kfitz.info", "2026-01-01")), path)
        assert hj.main(["revoke", "kfitz.info", "--file", str(path)]) == 0
        assert hj.load(path)["vouches"] == []

    def test_revoke_unknown_exits_nonzero(self, tmp_path):
        path = tmp_path / "human.json"
        hj.save(make_data(), path)
        assert hj.main(["revoke", "kfitz.info", "--file", str(path)]) != 0

    def test_renew_refreshes_the_date(self, tmp_path):
        path = tmp_path / "human.json"
        hj.save(make_data(("https://kfitz.info", "2026-01-01")), path)
        code = hj.main(
            ["renew", "kfitz.info", "--file", str(path), "--date", "2026-09-03"]
        )
        assert code == 0
        assert hj.load(path)["vouches"][0]["vouched_at"] == "2026-09-03"

    def test_renew_unknown_exits_nonzero(self, tmp_path):
        path = tmp_path / "human.json"
        hj.save(make_data(), path)
        assert (
            hj.main(
                ["renew", "kfitz.info", "--file", str(path), "--date", "2026-09-03"]
            )
            != 0
        )

    def test_date_defaults_to_today_when_omitted(self, tmp_path):
        path = tmp_path / "human.json"
        hj.main(["add", "kfitz.info", "--file", str(path)])
        today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        assert hj.load(path)["vouches"][0]["vouched_at"] == today

    def test_list_prints_vouches(self, tmp_path, capsys):
        path = tmp_path / "human.json"
        hj.save(
            make_data(
                ("https://kfitz.info", "2026-01-01"),
                ("https://brennan.day", "2026-01-02"),
            ),
            path,
        )
        assert hj.main(["list", "--file", str(path)]) == 0
        out = capsys.readouterr().out
        assert "https://kfitz.info" in out
        assert "2026-01-01" in out
        assert "https://brennan.day" in out
