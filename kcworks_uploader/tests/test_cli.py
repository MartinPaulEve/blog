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
    def test_publishes_draft_from_uploads_url(
        self, capsys, monkeypatch, tmp_path
    ):
        # Run outside any blog checkout so no kcworks_collection config
        # leaks in from the developer's real _config.yml.
        monkeypatch.chdir(tmp_path)
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


class FakeCollectionClient(FakeClient):
    """FakeClient plus the collection surface, scriptable per scenario."""

    def __init__(
        self,
        inclusion=None,
        record_ids=("coll-uuid",),
        accept_error=False,
    ):
        super().__init__()
        self.inclusion = (
            inclusion
            if inclusion is not None
            else {"processed": [{"request_id": "req1"}]}
        )
        self.record_ids = list(record_ids)
        self.accept_error = accept_error
        self.included = []
        self.accepted = []
        self.created = None

    def get_collection(self, slug):
        self.calls.append("get_collection")
        return {"id": "coll-uuid", "slug": slug}

    def add_to_collection(self, record_id, collection_id):
        self.calls.append("include")
        self.included.append((record_id, collection_id))
        return self.inclusion

    def accept_request(self, request_id):
        self.calls.append("accept")
        if self.accept_error:
            raise cli.KCWorksError("KC Works returned HTTP 400: no accept")
        self.accepted.append(request_id)
        return {"status": "accepted"}

    def get_record(self, record_id):
        self.calls.append("get_record")
        return {
            "id": record_id,
            "parent": {"communities": {"ids": self.record_ids}},
        }

    def create_collection(self, payload):
        self.calls.append("create_collection")
        self.created = payload
        return {"id": "coll-uuid", "slug": payload["slug"]}


class TestCollectionPayload:
    def test_carries_slug_title_and_public_visibility(self):
        payload = cli.collection_payload("evegd-blog-posts", "My Title")
        assert payload["slug"] == "evegd-blog-posts"
        assert payload["metadata"]["title"] == "My Title"
        assert payload["access"]["visibility"] == "public"

    def test_owner_can_publish_directly(self):
        payload = cli.collection_payload("s", "T")
        assert payload["access"]["review_policy"] == "open"

    def test_description_included_when_given(self):
        payload = cli.collection_payload("s", "T", description="About this")
        assert payload["metadata"]["description"] == "About this"


class TestIncludeInCollection:
    def test_accepted_inclusion_reports_included(self):
        client = FakeCollectionClient()
        assert cli.include_in_collection(client, "rec1", "coll-uuid") == (
            "included"
        )
        assert client.included == [("rec1", "coll-uuid")]
        assert client.accepted == ["req1"]

    def test_already_included_is_reported_without_error(self):
        client = FakeCollectionClient(
            inclusion={
                "processed": [],
                "errors": [
                    {"message": "The record is already in this community."}
                ],
            }
        )
        assert cli.include_in_collection(client, "rec1", "coll-uuid") == (
            "already"
        )

    def test_auto_accepted_request_still_counts_as_included(self):
        client = FakeCollectionClient(accept_error=True)
        assert cli.include_in_collection(client, "rec1", "coll-uuid") == (
            "included"
        )

    def test_pending_review_reports_requested(self):
        client = FakeCollectionClient(accept_error=True, record_ids=())
        assert cli.include_in_collection(client, "rec1", "coll-uuid") == (
            "requested"
        )

    def test_hard_failure_raises(self):
        client = FakeCollectionClient(
            inclusion={
                "processed": [],
                "errors": [{"message": "Permission denied"}],
            }
        )
        with pytest.raises(cli.KCWorksError):
            cli.include_in_collection(client, "rec1", "coll-uuid")


class TestEffectiveCollection:
    def test_override_wins(self, repo):
        (repo / "_config.yml").write_text("kcworks_collection: from-config\n")
        assert cli.effective_collection(repo, "explicit", False) == "explicit"

    def test_falls_back_to_blog_config(self, repo):
        (repo / "_config.yml").write_text("kcworks_collection: from-config\n")
        assert cli.effective_collection(repo, None, False) == "from-config"

    def test_disabled_gives_none(self, repo):
        (repo / "_config.yml").write_text("kcworks_collection: from-config\n")
        assert cli.effective_collection(repo, None, True) is None

    def test_no_config_gives_none(self, repo):
        assert cli.effective_collection(repo, None, False) is None


class TestUploadPostCollection:
    def test_live_upload_lands_in_the_collection(self, repo):
        client = FakeCollectionClient()
        result = upload_post(
            repo / "_posts" / "2026-08-28-a-test-post.md",
            client,
            live=True,
            collection="evegd-blog-posts",
        )
        assert result["collection"] == "included"
        assert client.calls.index("publish") < client.calls.index("include")

    def test_draft_upload_leaves_the_collection_for_publish_time(self, repo):
        client = FakeCollectionClient()
        result = upload_post(
            repo / "_posts" / "2026-08-28-a-test-post.md",
            client,
            live=False,
            collection="evegd-blog-posts",
        )
        assert "collection" not in result
        assert "include" not in client.calls

    def test_no_collection_means_no_inclusion(self, repo):
        client = FakeCollectionClient()
        result = upload_post(
            repo / "_posts" / "2026-08-28-a-test-post.md",
            client,
            live=True,
            collection=None,
        )
        assert "collection" not in result
        assert "include" not in client.calls


class TestPublishMainCollection:
    def test_publish_includes_into_the_given_collection(
        self, capsys, monkeypatch
    ):
        client = FakeCollectionClient()
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        code = publish_main(
            [
                "https://works.hcommons.org/uploads/abc12-xyz34",
                "--token",
                "tok",
                "--collection",
                "evegd-blog-posts",
            ]
        )
        assert code == 0
        assert client.included == [("abc12-xyz34", "coll-uuid")]
        assert "included" in capsys.readouterr().out

    def test_no_collection_publishes_without_inclusion(
        self, capsys, monkeypatch
    ):
        client = FakeCollectionClient()
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        monkeypatch.chdir("/")
        code = publish_main(
            [
                "https://works.hcommons.org/uploads/abc12-xyz34",
                "--token",
                "tok",
            ]
        )
        assert code == 0
        assert client.included == []


class TestCollectionMain:
    def test_create_posts_the_collection_and_prints_its_url(
        self, repo, capsys, monkeypatch
    ):
        client = FakeCollectionClient()
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        monkeypatch.chdir(repo)
        (repo / "_config.yml").write_text(
            "kcworks_collection: evegd-blog-posts\n"
        )
        code = cli.collection_main(
            ["create", "--title", "eve.gd blog posts", "--token", "tok"]
        )
        assert code == 0
        assert client.created["slug"] == "evegd-blog-posts"
        assert client.created["metadata"]["title"] == "eve.gd blog posts"
        assert "evegd-blog-posts" in capsys.readouterr().out

    def test_backfill_includes_every_deposited_post(
        self, repo, capsys, monkeypatch
    ):
        client = FakeCollectionClient()
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        monkeypatch.chdir(repo)
        (repo / "_config.yml").write_text(
            "kcworks_collection: evegd-blog-posts\n"
        )
        post = repo / "_posts" / "2026-08-28-a-test-post.md"
        post.write_text(
            POST_TEXT.replace(
                "---\nThe opening",
                "kcworks: https://works.hcommons.org/records/abc12-xyz34\n"
                "---\nThe opening",
            )
        )
        (repo / "_posts" / "2026-08-29-undeposited.md").write_text(
            "---\ntitle: No deposit\ndate: 2026-08-29\n---\nBody\n"
        )
        code = cli.collection_main(["backfill", "--token", "tok"])
        assert code == 0
        assert client.included == [("abc12-xyz34", "coll-uuid")]
        out = capsys.readouterr().out
        assert "abc12-xyz34" in out and "included" in out

    def test_missing_token_is_an_error(self, repo, capsys, monkeypatch):
        monkeypatch.chdir(repo)
        monkeypatch.delenv("KCWORKS_API_TOKEN", raising=False)
        assert cli.collection_main(["backfill"]) == 2
