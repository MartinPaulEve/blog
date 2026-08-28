import pytest

from kcworks_uploader.cli import deposit_url, main, upload_post

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


class TestDepositUrl:
    def test_derives_uploads_page_from_api_base(self):
        assert deposit_url("https://works.hcommons.org/api", "abc12") == (
            "https://works.hcommons.org/uploads/abc12"
        )


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
