import json
from pathlib import Path

import pytest
from kcworks_uploader.cli import (
    api_base_from_url,
    draft_id_from_url,
    main,
    publish_main,
    upload_post,
)
from kcworks_uploader.client import KCWorksConflict, KCWorksError

from kcworks_uploader import cli

POST_TEXT = """---
title: "A test post"
date: 2026-08-28
doi: https://doi.org/10.59348/abcde-f0123
tags:
- testing
---
The opening paragraph of the post.
"""

LIVE_URL = "https://works.hcommons.org/records/abc12-xyz34"


@pytest.fixture
def repo(tmp_path):
    """A miniature blog repo: _config.yml naming the collection, _posts,
    and a cached PDF for the post."""
    (tmp_path / "_posts").mkdir()
    (tmp_path / ".pdf_cache").mkdir()
    (tmp_path / "_config.yml").write_text(
        "kcworks_collection: evegd-blog-posts\n"
    )
    post = tmp_path / "_posts" / "2026-08-28-a-test-post.md"
    post.write_text(POST_TEXT)
    (tmp_path / ".pdf_cache" / "2026-08-28-a-test-post.pdf").write_bytes(
        b"%PDF-1.4"
    )
    return tmp_path


def imported(record_id="abc12-xyz34", paths=()):
    """The per-work entry the import API returns on success."""
    return {
        "item_index": 0,
        "record_id": record_id,
        "record_url": f"https://works.hcommons.org/records/{record_id}",
        "files": {Path(p).name: ["success", []] for p in paths},
        "collection_id": "coll-uuid",
        "errors": [],
        "metadata": {"id": record_id},
    }


class FakeClient:
    """A stand-in for KCWorksClient's import surface.

    Records every import_work call; answers with a canned success (or
    raises ``error`` when given)."""

    def __init__(
        self,
        base_url="https://works.hcommons.org/api",
        record_id="abc12-xyz34",
        error=None,
    ):
        self.base_url = base_url
        self.record_id = record_id
        self.error = error
        self.calls = []
        self.imports = []

    def import_work(self, collection, record, paths, review_required=False):
        self.calls.append("import")
        paths = [Path(p) for p in paths]
        self.imports.append((collection, record, paths, review_required))
        if self.error:
            raise self.error
        return imported(self.record_id, paths)

    @property
    def record(self):
        return self.imports[-1][1]

    def publish_draft(self, draft_id):
        self.calls.append("publish")
        return {
            "id": draft_id,
            "links": {
                "self_html": f"https://works.hcommons.org/records/{draft_id}"
            },
        }


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
    def run(self, repo, client=None, **kwargs):
        client = client or FakeClient()
        result = upload_post(
            repo / "_posts" / "2026-08-28-a-test-post.md",
            client,
            kwargs.pop("collection", "evegd-blog-posts"),
            **kwargs,
        )
        return result, client

    def test_returns_record_id_live_url_and_file_keys(self, repo):
        result, _ = self.run(repo)
        assert result["id"] == "abc12-xyz34"
        assert result["live_url"] == LIVE_URL
        assert result["files"] == [
            "2026-08-28-a-test-post.md",
            "2026-08-28-a-test-post.pdf",
        ]
        assert result["existing"] is False

    def test_imports_into_the_given_collection(self, repo):
        result, client = self.run(repo, collection="evegd-blog-posts")
        assert client.imports[0][0] == "evegd-blog-posts"
        assert result["collection"] == "coll-uuid"

    def test_sends_the_markdown_source_and_the_cached_pdf(self, repo):
        _, client = self.run(repo)
        assert client.imports[0][2] == [
            repo / "_posts" / "2026-08-28-a-test-post.md",
            repo / ".pdf_cache" / "2026-08-28-a-test-post.pdf",
        ]

    def test_never_asks_for_review(self, repo):
        _, client = self.run(repo)
        assert client.imports[0][3] is False

    def test_record_carries_post_metadata(self, repo):
        _, client = self.run(repo)
        md = client.record["metadata"]
        assert md["title"] == "A test post"
        assert {
            "identifier": "https://eve.gd/2026/08/28/a-test-post/",
            "scheme": "url",
        } in md["identifiers"]

    def test_record_is_keyed_by_the_post_slug_for_reimports(self, repo):
        _, client = self.run(repo)
        assert {
            "identifier": "2026-08-28-a-test-post",
            "scheme": "import-recid",
        } in client.record["metadata"]["identifiers"]

    def test_record_names_the_author_as_owner(self, repo):
        _, client = self.run(repo)
        owners = client.record["parent"]["access"]["owned_by"]
        assert owners[0]["email"] == "martin.eve@bbk.ac.uk"

    def test_record_lists_both_files_with_sizes(self, repo):
        _, client = self.run(repo)
        entries = client.record["files"]["entries"]
        assert entries["2026-08-28-a-test-post.pdf"]["size"] == len(b"%PDF-1.4")
        assert entries["2026-08-28-a-test-post.md"]["size"] == len(POST_TEXT)

    def test_pdf_is_the_default_preview_file(self, repo):
        _, client = self.run(repo)
        assert client.record["files"]["default_preview"] == (
            "2026-08-28-a-test-post.pdf"
        )

    def test_doi_is_an_external_pid_by_default(self, repo):
        _, client = self.run(repo)
        assert client.record["pids"]["doi"] == {
            "identifier": "10.59348/abcde-f0123",
            "provider": "external",
        }

    def test_include_doi_false_omits_pids(self, repo):
        _, client = self.run(repo, include_doi=False)
        assert "pids" not in client.record

    def test_explicit_pdf_path_is_used(self, repo):
        other = repo / "other.pdf"
        other.write_bytes(b"%PDF-1.7 other")
        result, client = self.run(repo, pdf_path=other)
        assert client.imports[0][2][1] == other
        assert result["files"] == ["2026-08-28-a-test-post.md", "other.pdf"]

    def test_missing_pdf_raises_before_any_import(self, repo):
        (repo / ".pdf_cache" / "2026-08-28-a-test-post.pdf").unlink()
        client = FakeClient()
        with pytest.raises(FileNotFoundError):
            self.run(repo, client)
        assert client.calls == []

    def test_conflict_resolves_to_the_existing_record(self, repo):
        existing = "https://works.hcommons.org/records/old11-old11"
        client = FakeClient(
            error=KCWorksConflict("already exists", location=existing)
        )
        result, _ = self.run(repo, client)
        assert result["id"] == "old11-old11"
        assert result["live_url"] == existing
        assert result["existing"] is True

    def test_conflict_without_a_location_is_an_error(self, repo):
        client = FakeClient(error=KCWorksConflict("already exists"))
        with pytest.raises(KCWorksError):
            self.run(repo, client)

    def test_server_errors_propagate(self, repo):
        client = FakeClient(error=KCWorksError("HTTP 403: permissions"))
        with pytest.raises(KCWorksError, match="permissions"):
            self.run(repo, client)


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
    def test_dry_run_prints_record_without_uploading(
        self, repo, capsys, monkeypatch
    ):
        monkeypatch.setattr(
            cli,
            "KCWorksClient",
            lambda *a, **k: pytest.fail("dry-run must not touch the network"),
        )
        rc = main(
            [str(repo / "_posts" / "2026-08-28-a-test-post.md"), "--dry-run"]
        )
        out = capsys.readouterr().out
        assert rc == 0
        record = json.loads(out[out.index("{") : out.rindex("}") + 1])
        assert record["metadata"]["resource_type"]["id"] == (
            "textDocument-blogPost"
        )
        assert record["parent"]["access"]["owned_by"][0]["full_name"] == (
            "Martin Paul Eve"
        )
        assert "2026-08-28-a-test-post.pdf" in record["files"]["entries"]

    def test_dry_run_without_a_pdf_still_prints_the_record(
        self, repo, capsys
    ):
        (repo / ".pdf_cache" / "2026-08-28-a-test-post.pdf").unlink()
        rc = main(
            [str(repo / "_posts" / "2026-08-28-a-test-post.md"), "--dry-run"]
        )
        captured = capsys.readouterr()
        assert rc == 0
        assert "textDocument-blogPost" in captured.out
        assert "PDF" in captured.err

    def test_missing_token_is_an_error(self, repo, capsys, monkeypatch):
        monkeypatch.delenv("KCWORKS_API_TOKEN", raising=False)
        rc = main([str(repo / "_posts" / "2026-08-28-a-test-post.md")])
        assert rc == 2
        assert "token" in capsys.readouterr().err.lower()

    def test_deposit_publishes_and_stamps_record_url_into_post(
        self, repo, capsys, monkeypatch
    ):
        client = FakeClient()
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        post = repo / "_posts" / "2026-08-28-a-test-post.md"
        rc = main([str(post), "--token", "tok"])
        assert rc == 0
        assert f"\nkcworks: {LIVE_URL}\n" in post.read_text()
        out = capsys.readouterr().out
        assert LIVE_URL in out
        assert "front matter" in out.lower()
        assert client.imports[0][0] == "evegd-blog-posts"

    def test_collection_comes_from_the_blog_config_by_default(
        self, repo, monkeypatch
    ):
        client = FakeClient()
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        monkeypatch.chdir("/")
        post = repo / "_posts" / "2026-08-28-a-test-post.md"
        assert main([str(post), "--token", "tok"]) == 0
        assert client.imports[0][0] == "evegd-blog-posts"

    def test_collection_override(self, repo, monkeypatch):
        client = FakeClient()
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        post = repo / "_posts" / "2026-08-28-a-test-post.md"
        rc = main([str(post), "--token", "tok", "--collection", "other-coll"])
        assert rc == 0
        assert client.imports[0][0] == "other-coll"

    def test_no_collection_configured_is_an_error(
        self, repo, capsys, monkeypatch
    ):
        (repo / "_config.yml").write_text("title: no collection here\n")
        client = FakeClient()
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        post = repo / "_posts" / "2026-08-28-a-test-post.md"
        rc = main([str(post), "--token", "tok"])
        assert rc == 2
        assert "collection" in capsys.readouterr().err.lower()
        assert client.calls == []
        assert "kcworks:" not in post.read_text()

    def test_server_error_leaves_the_post_untouched(
        self, repo, capsys, monkeypatch
    ):
        client = FakeClient(error=KCWorksError("HTTP 403: permissions"))
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        post = repo / "_posts" / "2026-08-28-a-test-post.md"
        before = post.read_text()
        rc = main([str(post), "--token", "tok"])
        assert rc == 1
        assert post.read_text() == before
        assert "permissions" in capsys.readouterr().err

    def test_existing_record_is_stamped_too(self, repo, capsys, monkeypatch):
        existing = "https://works.hcommons.org/records/old11-old11"
        client = FakeClient(
            error=KCWorksConflict("already exists", location=existing)
        )
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        post = repo / "_posts" / "2026-08-28-a-test-post.md"
        rc = main([str(post), "--token", "tok"])
        assert rc == 0
        assert f"kcworks: {existing}" in post.read_text()
        assert "already" in capsys.readouterr().out.lower()

    def test_live_flag_is_still_accepted(self, repo, monkeypatch):
        client = FakeClient()
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        post = repo / "_posts" / "2026-08-28-a-test-post.md"
        assert main([str(post), "--live", "--token", "tok"]) == 0
        assert client.calls == ["import"]


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

    def upload_collection_logo(self, collection_id, path):
        self.calls.append("logo")
        self.logo = (collection_id, path)
        return {"size": path.stat().st_size}


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

    def test_no_config_gives_none(self, tmp_path):
        assert cli.effective_collection(tmp_path, None, False) is None



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


@pytest.fixture
def backfill_repo(tmp_path):
    """A blog with two pending posts, one deposited post, and their PDFs."""
    (tmp_path / "_posts").mkdir()
    (tmp_path / ".pdf_cache").mkdir()
    (tmp_path / "_config.yml").write_text(
        "kcworks_collection: evegd-blog-posts\n"
    )
    for name in ("2026-01-01-first", "2026-02-02-second"):
        (tmp_path / "_posts" / f"{name}.md").write_text(
            f"---\ntitle: {name}\n---\nBody of {name}.\n"
        )
        (tmp_path / ".pdf_cache" / f"{name}.pdf").write_bytes(b"%PDF-1.4")
    (tmp_path / "_posts" / "2025-12-31-deposited.md").write_text(
        "---\ntitle: Deposited\nkcworks: https://works.hcommons.org/"
        "records/old11-old11\n---\nAlready archived.\n"
    )
    return tmp_path




class TestBackfillMain:
    def run(self, monkeypatch, repo, client, argv=()):
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        monkeypatch.chdir(repo)
        return cli.backfill_main(
            ["--token", "tok", "--delay", "0", *argv]
        )

    def log_entries(self, repo):
        return [
            json.loads(line)
            for line in (repo / "kcworks-backfill.log").read_text().splitlines()
        ]

    def test_dry_run_lists_pending_posts_without_a_token(
        self, backfill_repo, capsys, monkeypatch
    ):
        monkeypatch.chdir(backfill_repo)
        monkeypatch.delenv("KCWORKS_API_TOKEN", raising=False)
        monkeypatch.setattr(
            cli,
            "KCWorksClient",
            lambda *a, **k: pytest.fail("dry-run must not touch the network"),
        )
        assert cli.backfill_main(["--dry-run"]) == 0
        out = capsys.readouterr().out
        assert "2026-01-01-first.md" in out
        assert "2026-02-02-second.md" in out
        assert "2025-12-31-deposited.md" not in out

    def test_publishes_and_stamps_every_pending_post(
        self, backfill_repo, capsys, monkeypatch
    ):
        client = FakeClient()
        code = self.run(monkeypatch, backfill_repo, client)
        assert code == 0
        for name in ("2026-01-01-first", "2026-02-02-second"):
            text = (backfill_repo / "_posts" / f"{name}.md").read_text()
            assert f"kcworks: {LIVE_URL}" in text
            assert f"Body of {name}." in text
        assert (
            backfill_repo / "_posts" / "2025-12-31-deposited.md"
        ).read_text().count("kcworks:") == 1
        assert client.calls == ["import", "import"]

    def test_records_land_in_the_configured_collection(
        self, backfill_repo, monkeypatch
    ):
        client = FakeClient()
        assert self.run(monkeypatch, backfill_repo, client) == 0
        assert [i[0] for i in client.imports] == [
            "evegd-blog-posts",
            "evegd-blog-posts",
        ]

    def test_collection_override(self, backfill_repo, monkeypatch):
        client = FakeClient()
        code = self.run(
            monkeypatch, backfill_repo, client, ["--collection", "other"]
        )
        assert code == 0
        assert {i[0] for i in client.imports} == {"other"}

    def test_no_collection_configured_is_an_error(
        self, backfill_repo, capsys, monkeypatch
    ):
        (backfill_repo / "_config.yml").write_text("title: none\n")
        client = FakeClient()
        assert self.run(monkeypatch, backfill_repo, client) == 2
        assert "collection" in capsys.readouterr().err.lower()
        assert client.calls == []

    def test_every_outcome_is_logged_as_json_lines(
        self, backfill_repo, monkeypatch
    ):
        client = FakeClient()
        self.run(monkeypatch, backfill_repo, client)
        entries = self.log_entries(backfill_repo)
        assert [e["post"] for e in entries] == [
            "2026-01-01-first.md",
            "2026-02-02-second.md",
        ]
        assert all(e["status"] == "published" for e in entries)
        assert all(e["live_url"] == LIVE_URL for e in entries)
        assert all(e["collection"] == "coll-uuid" for e in entries)
        assert all(e["time"] for e in entries)

    def test_failure_is_logged_and_the_run_continues(
        self, backfill_repo, capsys, monkeypatch
    ):
        (backfill_repo / ".pdf_cache" / "2026-01-01-first.pdf").unlink()
        client = FakeClient()
        code = self.run(monkeypatch, backfill_repo, client)
        assert code == 1
        first = (backfill_repo / "_posts" / "2026-01-01-first.md").read_text()
        assert "kcworks:" not in first
        second = (
            backfill_repo / "_posts" / "2026-02-02-second.md"
        ).read_text()
        assert f"kcworks: {LIVE_URL}" in second
        entries = self.log_entries(backfill_repo)
        assert entries[0]["status"] == "failed"
        assert "PDF" in entries[0]["error"]
        assert entries[1]["status"] == "published"
        out = capsys.readouterr().out
        assert "2026-01-01-first.md" in out
        assert "1 failed" in out

    def test_server_rejection_is_logged_with_its_message(
        self, backfill_repo, monkeypatch
    ):
        client = FakeClient(error=KCWorksError("HTTP 400: Required field missing."))
        code = self.run(monkeypatch, backfill_repo, client)
        assert code == 1
        entries = self.log_entries(backfill_repo)
        assert [e["status"] for e in entries] == ["failed", "failed"]
        assert "Required field missing" in entries[0]["error"]

    def test_existing_record_conflict_stamps_the_post(
        self, backfill_repo, monkeypatch
    ):
        existing = "https://works.hcommons.org/records/old11-old11"
        client = FakeClient(
            error=KCWorksConflict("already exists", location=existing)
        )
        code = self.run(monkeypatch, backfill_repo, client, ["--limit", "1"])
        assert code == 0
        assert f"kcworks: {existing}" in (
            backfill_repo / "_posts" / "2026-01-01-first.md"
        ).read_text()
        entry = self.log_entries(backfill_repo)[0]
        assert entry["status"] == "existing"
        assert entry["live_url"] == existing

    def test_waits_between_deposits(self, backfill_repo, monkeypatch):
        naps = []
        monkeypatch.setattr(cli.time, "sleep", naps.append)
        client = FakeClient()
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        monkeypatch.chdir(backfill_repo)
        cli.backfill_main(["--token", "tok", "--delay", "7"])
        assert naps == [7.0]

    def test_limit_caps_the_run(self, backfill_repo, monkeypatch):
        client = FakeClient()
        code = self.run(monkeypatch, backfill_repo, client, ["--limit", "1"])
        assert code == 0
        assert "kcworks:" in (
            backfill_repo / "_posts" / "2026-01-01-first.md"
        ).read_text()
        assert "kcworks:" not in (
            backfill_repo / "_posts" / "2026-02-02-second.md"
        ).read_text()

    def test_missing_token_is_an_error(
        self, backfill_repo, capsys, monkeypatch
    ):
        monkeypatch.chdir(backfill_repo)
        monkeypatch.delenv("KCWORKS_API_TOKEN", raising=False)
        assert cli.backfill_main([]) == 2
        assert "token" in capsys.readouterr().err.lower()

    def test_nothing_pending_is_a_clean_no_op(
        self, backfill_repo, capsys, monkeypatch
    ):
        for name in ("2026-01-01-first", "2026-02-02-second"):
            path = backfill_repo / "_posts" / f"{name}.md"
            path.write_text(
                path.read_text().replace(
                    "---\nBody",
                    f"kcworks: {LIVE_URL}\n---\nBody",
                )
            )
        client = FakeClient()
        assert self.run(monkeypatch, backfill_repo, client) == 0
        assert client.calls == []


class TestCollectionMainLogo:
    def test_uploads_the_logo_to_the_configured_collection(
        self, repo, capsys, monkeypatch
    ):
        client = FakeCollectionClient()
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        monkeypatch.chdir(repo)
        (repo / "_config.yml").write_text(
            "kcworks_collection: evegd-blog-posts\n"
        )
        icon = repo / "icon.png"
        icon.write_bytes(b"\x89PNG bytes")
        code = cli.collection_main(["logo", str(icon), "--token", "tok"])
        assert code == 0
        assert client.logo == ("coll-uuid", icon)
        assert "logo" in capsys.readouterr().out.lower()

    def test_missing_image_is_an_error(self, repo, capsys, monkeypatch):
        monkeypatch.setattr(
            cli, "KCWorksClient", lambda *a, **k: FakeCollectionClient()
        )
        monkeypatch.chdir(repo)
        (repo / "_config.yml").write_text(
            "kcworks_collection: evegd-blog-posts\n"
        )
        code = cli.collection_main(
            ["logo", str(repo / "missing.png"), "--token", "tok"]
        )
        assert code == 1
        assert "missing.png" in capsys.readouterr().err


UPDATED_POST_TEXT = """---
title: "An updated post"
date: 2026-08-28
doi: https://doi.org/10.59348/abcde-f0123
kcworks: https://works.hcommons.org/records/old11-old22
last_modified_at: 2026-09-06
---
The opening paragraph of the post.
"""




class FakeUpdateClient(FakeClient):
    """FakeClient plus the record lookup the update flow starts with."""

    def __init__(
        self,
        record_updated="2026-09-01T10:00:00.000000+00:00",
        record_id="new33-new44",
        error=None,
    ):
        super().__init__(record_id=record_id, error=error)
        self.record_updated = record_updated

    def get_record(self, record_id):
        self.calls.append("get_record")
        self.looked_up = record_id
        return {"id": record_id, "updated": self.record_updated}


class TestNeedsUpdate:
    def test_record_older_than_post_needs_update(self):
        assert cli.needs_update(
            {"updated": "2026-09-01T10:00:00.000000+00:00"}, "2026-09-06"
        ) is True

    def test_record_from_the_same_day_or_later_does_not(self):
        assert cli.needs_update(
            {"updated": "2026-09-06T00:10:00.000000+00:00"}, "2026-09-06"
        ) is False
        assert cli.needs_update(
            {"updated": "2026-10-01T00:00:00.000000+00:00"}, "2026-09-06"
        ) is False

    def test_unknown_record_state_needs_update(self):
        assert cli.needs_update({}, "2026-09-06") is True




class TestUpdateMain:
    @pytest.fixture
    def updated_repo(self, tmp_path):
        (tmp_path / "_posts").mkdir()
        (tmp_path / ".pdf_cache").mkdir()
        (tmp_path / "_config.yml").write_text(
            "kcworks_collection: evegd-blog-posts\n"
        )
        post = tmp_path / "_posts" / "2026-08-28-a-test-post.md"
        post.write_text(UPDATED_POST_TEXT)
        (tmp_path / ".pdf_cache" / "2026-08-28-a-test-post.pdf").write_bytes(
            b"%PDF-1.4"
        )
        return tmp_path

    def run(self, monkeypatch, repo, client, argv=()):
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        monkeypatch.chdir(repo)
        post = repo / "_posts" / "2026-08-28-a-test-post.md"
        return cli.update_main([str(post), "--token", "tok", *argv]), post

    def test_stale_deposit_is_reimported_and_restamped(
        self, updated_repo, capsys, monkeypatch
    ):
        client = FakeUpdateClient()
        rc, post = self.run(monkeypatch, updated_repo, client)
        assert rc == 0
        assert client.looked_up == "old11-old22"
        assert client.calls == ["get_record", "import"]
        text = post.read_text()
        assert "kcworks: https://works.hcommons.org/records/new33-new44\n" in text
        assert "old11-old22" not in text

    def test_reimport_targets_the_configured_collection(
        self, updated_repo, monkeypatch
    ):
        client = FakeUpdateClient()
        self.run(monkeypatch, updated_repo, client)
        assert client.imports[0][0] == "evegd-blog-posts"

    def test_reimport_keeps_the_identifiers_that_match_the_record(
        self, updated_repo, monkeypatch
    ):
        # The import API matches an existing work by its DOI pid and the
        # import-recid identifier, then updates it in place -- so both
        # must be sent exactly as the original deposit sent them.
        client = FakeUpdateClient()
        self.run(monkeypatch, updated_repo, client)
        record = client.record
        assert record["pids"]["doi"] == {
            "identifier": "10.59348/abcde-f0123",
            "provider": "external",
        }
        assert {
            "identifier": "2026-08-28-a-test-post",
            "scheme": "import-recid",
        } in record["metadata"]["identifiers"]

    def test_reimport_sends_the_current_markdown_and_pdf(
        self, updated_repo, monkeypatch
    ):
        client = FakeUpdateClient()
        self.run(monkeypatch, updated_repo, client)
        assert [p.name for p in client.imports[0][2]] == [
            "2026-08-28-a-test-post.md",
            "2026-08-28-a-test-post.pdf",
        ]
        assert client.record["metadata"]["dates"] == [
            {"date": "2026-09-06", "type": {"id": "updated"}}
        ]

    def test_fresh_deposit_is_skipped(
        self, updated_repo, capsys, monkeypatch
    ):
        client = FakeUpdateClient(record_updated="2026-09-07T00:00:00+00:00")
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        monkeypatch.chdir(updated_repo)
        post = updated_repo / "_posts" / "2026-08-28-a-test-post.md"
        before = post.read_text()
        rc, _ = self.run(monkeypatch, updated_repo, client)
        assert rc == 0
        assert "import" not in client.calls
        assert post.read_text() == before

    def test_failed_reimport_is_logged_and_leaves_the_stamp(
        self, updated_repo, capsys, monkeypatch
    ):
        client = FakeUpdateClient(error=KCWorksConflict("refused"))
        rc, post = self.run(monkeypatch, updated_repo, client)
        assert rc == 1
        assert "old11-old22" in post.read_text()
        entry = json.loads(
            (updated_repo / "kcworks-update.log").read_text().splitlines()[0]
        )
        assert entry["status"] == "failed"
        assert "refused" in entry["error"]

    def test_no_collection_configured_is_an_error(
        self, updated_repo, capsys, monkeypatch
    ):
        (updated_repo / "_config.yml").write_text("title: none\n")
        client = FakeUpdateClient()
        rc, _ = self.run(monkeypatch, updated_repo, client)
        assert rc == 2
        assert "collection" in capsys.readouterr().err.lower()
        assert client.calls == []

    def test_dry_run_contacts_nothing_and_changes_nothing(
        self, updated_repo, capsys, monkeypatch
    ):
        client = FakeUpdateClient()
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        monkeypatch.chdir(updated_repo)
        post = updated_repo / "_posts" / "2026-08-28-a-test-post.md"
        before = post.read_text()
        rc = cli.update_main([str(post), "--token", "tok", "--dry-run"])
        assert rc == 0
        assert client.calls == []
        assert post.read_text() == before

    def test_post_without_kcworks_or_lastmod_is_skipped(
        self, repo, capsys, monkeypatch
    ):
        client = FakeUpdateClient()
        monkeypatch.setattr(cli, "KCWorksClient", lambda *a, **k: client)
        monkeypatch.chdir(repo)
        post = repo / "_posts" / "2026-08-28-a-test-post.md"
        rc = cli.update_main([str(post), "--token", "tok"])
        assert rc == 0
        assert client.calls == []
