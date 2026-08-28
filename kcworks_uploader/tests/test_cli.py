import pytest

from kcworks_uploader import cli
from kcworks_uploader.cli import (
    api_base_from_url,
    deposit_url,
    draft_id_from_url,
    main,
    publish_main,
    upload_post,
)

POST_TEXT = """---
title: "A test post"
date: 2026-08-28
doi: https://doi.org/10.59348/abcde-f0123
tags:
- testing
---
The opening paragraph of the post.
"""


@pytest.fixture
def repo(tmp_path):
    """A miniature blog repo: _posts plus a cached PDF for the post."""
    (tmp_path / "_posts").mkdir()
    (tmp_path / ".pdf_cache").mkdir()
    post = tmp_path / "_posts" / "2026-08-28-a-test-post.md"
    post.write_text(POST_TEXT)
    (tmp_path / ".pdf_cache" / "2026-08-28-a-test-post.pdf").write_bytes(
        b"%PDF-1.4"
    )
    return tmp_path


class FakeClient:
    def __init__(self, base_url="https://works.hcommons.org/api"):
        self.base_url = base_url
        self.record = None
        self.uploaded = None
        self.updated_record = None
        self.calls = []

    def create_draft(self, record):
        self.calls.append("create")
        self.record = record
        return {"id": "abc12-xyz34", "links": {}}

    def upload_files(self, draft_id, paths):
        self.calls.append("upload")
        self.uploaded = (draft_id, list(paths))
        return [p.name for p in paths]

    def update_draft(self, draft_id, record):
        self.calls.append("update")
        self.updated_record = record
        return {"id": draft_id, "files": dict(record.get("files", {}))}

    def publish_draft(self, draft_id):
        self.calls.append("publish")
        return {
            "id": draft_id,
            "links": {
                "self_html": f"https://works.hcommons.org/records/{draft_id}"
            },
        }


class TestDepositUrl:
    def test_derives_uploads_page_from_api_base(self):
        assert deposit_url("https://works.hcommons.org/api", "abc12") == (
            "https://works.hcommons.org/uploads/abc12"
        )


class TestDraftIdFromUrl:
    def test_extracts_id_from_uploads_url(self):
        assert draft_id_from_url(
            "https://works.hcommons.org/uploads/abc12-xyz34"
        ) == "abc12-xyz34"

    def test_tolerates_trailing_slash(self):
        assert draft_id_from_url(
            "https://works.hcommons.org/uploads/abc12-xyz34/"
        ) == "abc12-xyz34"

    def test_accepts_records_url(self):
        assert draft_id_from_url(
            "https://works.hcommons.org/records/abc12-xyz34"
        ) == "abc12-xyz34"

    def test_accepts_bare_id(self):
        assert draft_id_from_url("abc12-xyz34") == "abc12-xyz34"


class TestApiBaseFromUrl:
    def test_derived_from_kc_works_url(self):
        assert api_base_from_url(
            "https://works.hcommons.org/uploads/abc12-xyz34"
        ) == "https://works.hcommons.org/api"

    def test_bare_id_gives_none(self):
        assert api_base_from_url("abc12-xyz34") is None


class TestUploadPost:
    def test_returns_draft_id_edit_url_and_file_keys(self, repo):
        result = upload_post(
            repo / "_posts" / "2026-08-28-a-test-post.md", FakeClient()
        )
        assert result["id"] == "abc12-xyz34"
        assert result["edit_url"] == (
            "https://works.hcommons.org/uploads/abc12-xyz34"
        )
        assert result["files"] == [
            "2026-08-28-a-test-post.md",
            "2026-08-28-a-test-post.pdf",
        ]

    def test_record_carries_post_metadata(self, repo):
        client = FakeClient()
        upload_post(repo / "_posts" / "2026-08-28-a-test-post.md", client)
        md = client.record["metadata"]
        assert md["title"] == "A test post"
        assert {
            "identifier": "https://eve.gd/2026/08/28/a-test-post/",
            "scheme": "url",
        } in md["identifiers"]

    def test_pdf_is_the_default_preview_file(self, repo):
        client = FakeClient()
        upload_post(repo / "_posts" / "2026-08-28-a-test-post.md", client)
        assert client.record["files"]["default_preview"] == (
            "2026-08-28-a-test-post.pdf"
        )

    def test_default_preview_reasserted_after_files_exist(self, repo):
        # InvenioRDM drops default_preview at creation time (the file does
        # not exist yet), so the draft must be updated again after the
        # uploads are committed for the Files tab to honour it.
        client = FakeClient()
        result = upload_post(
            repo / "_posts" / "2026-08-28-a-test-post.md", client
        )
        assert client.calls == ["create", "upload", "update"]
        assert client.updated_record["files"]["default_preview"] == (
            "2026-08-28-a-test-post.pdf"
        )
        assert result["record"]["files"]["default_preview"] == (
            "2026-08-28-a-test-post.pdf"
        )

    def test_include_doi_false_omits_pids(self, repo):
        client = FakeClient()
        upload_post(
            repo / "_posts" / "2026-08-28-a-test-post.md",
            client,
            include_doi=False,
        )
        assert "pids" not in client.record

    def test_missing_pdf_raises(self, repo):
        (repo / ".pdf_cache" / "2026-08-28-a-test-post.pdf").unlink()
        with pytest.raises(FileNotFoundError):
            upload_post(
                repo / "_posts" / "2026-08-28-a-test-post.md", FakeClient()
            )


class TestUploadPostLive:
    def test_live_publishes_after_the_preview_update(self, repo):
        client = FakeClient()
        result = upload_post(
            repo / "_posts" / "2026-08-28-a-test-post.md", client, live=True
        )
        assert client.calls == ["create", "upload", "update", "publish"]
        assert result["published"] is True
        assert result["live_url"] == (
            "https://works.hcommons.org/records/abc12-xyz34"
        )

    def test_draft_remains_the_default(self, repo):
        client = FakeClient()
        result = upload_post(
            repo / "_posts" / "2026-08-28-a-test-post.md", client
        )
        assert "publish" not in client.calls
        assert result["published"] is False


class TestPublishMain:
    def test_publishes_draft_from_uploads_url(self, capsys, monkeypatch):
        seen = {}

        class FakePublishingClient:
            def __init__(self, base_url, token):
                seen["base_url"] = base_url
                seen["token"] = token
                self.base_url = base_url

            def publish_draft(self, draft_id):
                seen["draft_id"] = draft_id
                return {
                    "id": draft_id,
                    "links": {
                        "self_html": (
                            "https://works.hcommons.org/records/" + draft_id
                        )
                    },
                }

        monkeypatch.setattr(cli, "KCWorksClient", FakePublishingClient)
        rc = publish_main(
            ["https://works.hcommons.org/uploads/abc12-xyz34", "--token", "t"]
        )
        assert rc == 0
        assert seen["draft_id"] == "abc12-xyz34"
        assert seen["base_url"] == "https://works.hcommons.org/api"
        assert seen["token"] == "t"
        assert "https://works.hcommons.org/records/abc12-xyz34" in (
            capsys.readouterr().out
        )

    def test_missing_token_is_an_error(self, capsys, monkeypatch):
        monkeypatch.delenv("KCWORKS_API_TOKEN", raising=False)
        rc = publish_main(["abc12-xyz34"])
        assert rc == 2
        assert "token" in capsys.readouterr().err.lower()


class TestMain:
    def test_dry_run_prints_record_without_uploading(self, repo, capsys):
        rc = main(
            [str(repo / "_posts" / "2026-08-28-a-test-post.md"), "--dry-run"]
        )
        out = capsys.readouterr().out
        assert rc == 0
        assert "textDocument-blogPost" in out

    def test_missing_token_is_an_error(self, repo, capsys, monkeypatch):
        monkeypatch.delenv("KCWORKS_API_TOKEN", raising=False)
        rc = main([str(repo / "_posts" / "2026-08-28-a-test-post.md")])
        assert rc == 2
        assert "token" in capsys.readouterr().err.lower()
