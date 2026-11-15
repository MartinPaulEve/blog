from pathlib import Path

import pytest
from kcworks_uploader.metadata import build_metadata
from kcworks_uploader.posts import Post

URL = "https://eve.gd/2026/08/28/repository-metadata/"


@pytest.fixture
def post():
    return Post(
        path=Path("/x/_posts/2026-08-28-repository-metadata.md"),
        title="Repository metadata contain ontological ambiguities",
        date="2026-08-28",
        doi="10.59348/mjvdw-w0051",
        tags=["metadata", "repositories"],
        body="An opening paragraph.\n\nMore text.\n",
    )


class TestRecordShape:
    def test_resource_type_is_blog_post(self, post):
        record = build_metadata(post, URL)
        assert record["metadata"]["resource_type"] == {
            "id": "textDocument-blogPost"
        }

    def test_title_and_publication_date(self, post):
        md = build_metadata(post, URL)["metadata"]
        assert md["title"] == post.title
        assert md["publication_date"] == "2026-08-28"

    def test_description_is_first_paragraph(self, post):
        md = build_metadata(post, URL)["metadata"]
        assert md["description"] == "An opening paragraph."

    def test_publisher_and_language(self, post):
        md = build_metadata(post, URL)["metadata"]
        assert md["publisher"] == "Martin Paul Eve"
        assert md["languages"] == [{"id": "eng"}]

    def test_cc_by_licence(self, post):
        md = build_metadata(post, URL)["metadata"]
        assert md["rights"] == [{"id": "cc-by-4.0"}]

    def test_canonical_url_identifier(self, post):
        md = build_metadata(post, URL)["metadata"]
        assert {"identifier": URL, "scheme": "url"} in md["identifiers"]

    def test_files_enabled_and_public_access(self, post):
        record = build_metadata(post, URL)
        assert record["files"] == {"enabled": True}
        assert record["access"] == {"record": "public", "files": "public"}

    def test_without_files_only_enabled_is_set(self, post):
        assert build_metadata(post, URL)["files"] == {"enabled": True}


class TestBlogDetails:
    def test_blog_title(self, post):
        custom = build_metadata(post, URL)["custom_fields"]
        assert custom["journal:journal"] == {
            "title": "eve.gd: Martin Paul Eve"
        }

    def test_blog_url(self, post):
        custom = build_metadata(post, URL)["custom_fields"]
        assert custom["kcr:publication_url"] == "https://eve.gd"

    def test_blog_publisher_location(self, post):
        custom = build_metadata(post, URL)["custom_fields"]
        assert custom["imprint:imprint"] == {"place": "United Kingdom"}

    def test_ai_contribution_declared(self, post):
        custom = build_metadata(post, URL)["custom_fields"]
        assert custom["kcr:ai_usage"] == {
            "ai_used": True,
            "ai_description": (
                "All words written in this post were written by hand, by a "
                "human (the author). No generative AI was used in the "
                "production of the writing. The technical infrastructure "
                "that builds the blog and PDFs was assisted by AI coding "
                "from Claude. The full AI usage policy is available here: "
                "https://eve.gd/ai/"
            ),
        }


class TestCreator:
    def test_single_personal_creator_named_eve(self, post):
        creators = build_metadata(post, URL)["metadata"]["creators"]
        assert len(creators) == 1
        person = creators[0]["person_or_org"]
        assert person["type"] == "personal"
        assert person["family_name"] == "Eve"
        assert person["given_name"] == "Martin Paul"
        assert creators[0]["role"] == {"id": "author"}

    def test_identifiers_include_kc_username_orcid_and_email(self, post):
        person = build_metadata(post, URL)["metadata"]["creators"][0][
            "person_or_org"
        ]
        assert {"identifier": "martin_eve", "scheme": "kc_username"} in (
            person["identifiers"]
        )
        assert {
            "identifier": "0000-0002-5589-8511",
            "scheme": "orcid",
        } in person["identifiers"]
        assert {
            "identifier": "martin.eve@bbk.ac.uk",
            "scheme": "email",
        } in person["identifiers"]

    def test_two_separate_affiliations(self, post):
        creator = build_metadata(post, URL)["metadata"]["creators"][0]
        assert creator["affiliations"] == [
            {"name": "Birkbeck, University of London"},
            {"name": "Michigan State University"},
        ]


class TestDoiAndTags:
    def test_doi_becomes_external_pid(self, post):
        record = build_metadata(post, URL)
        assert record["pids"] == {
            "doi": {
                "identifier": "10.59348/mjvdw-w0051",
                "provider": "external",
            }
        }

    def test_include_doi_false_omits_pids(self, post):
        assert "pids" not in build_metadata(post, URL, include_doi=False)

    def test_post_without_doi_omits_pids(self, post):
        post.doi = None
        assert "pids" not in build_metadata(post, URL)

    def test_tags_become_user_defined_tags(self, post):
        record = build_metadata(post, URL)
        assert record["custom_fields"]["kcr:user_defined_tags"] == [
            "metadata",
            "repositories",
        ]

    def test_no_tags_omits_user_defined_tags(self, post):
        post.tags = []
        custom = build_metadata(post, URL)["custom_fields"]
        assert "kcr:user_defined_tags" not in custom


class TestUpdatedDate:
    def test_last_modified_becomes_an_updated_date_entry(self, post):
        post.last_modified = "2026-09-06"
        record = build_metadata(post, URL)
        assert record["metadata"]["dates"] == [
            {"date": "2026-09-06", "type": {"id": "updated"}}
        ]

    def test_no_last_modified_means_no_dates_key(self, post):
        record = build_metadata(post, URL)
        assert "dates" not in record["metadata"]


class TestOwner:
    def test_author_owns_the_work(self, post):
        owners = build_metadata(post, URL)["parent"]["access"]["owned_by"]
        assert len(owners) == 1
        owner = owners[0]
        assert owner["full_name"] == "Martin Paul Eve"
        assert owner["email"] == "martin.eve@bbk.ac.uk"
        assert {"identifier": "martin_eve", "scheme": "kc_username"} in (
            owner["identifiers"]
        )
        assert {"identifier": "0000-0002-5589-8511", "scheme": "orcid"} in (
            owner["identifiers"]
        )

    def test_owner_is_the_creator(self, post):
        record = build_metadata(post, URL)
        creator = record["metadata"]["creators"][0]["person_or_org"]
        owner = record["parent"]["access"]["owned_by"][0]
        creator_ids = {
            (i["scheme"], i["identifier"]) for i in creator["identifiers"]
        }
        owner_ids = {(i["scheme"], i["identifier"]) for i in owner["identifiers"]}
        assert owner_ids <= creator_ids
        assert owner["full_name"] == (
            f"{creator['given_name']} {creator['family_name']}"
        )


@pytest.fixture
def paths(tmp_path):
    md = tmp_path / "2026-08-28-repository-metadata.md"
    md.write_text("---\ntitle: x\n---\nhello")
    pdf = tmp_path / "2026-08-28-repository-metadata.pdf"
    pdf.write_bytes(b"%PDF-1.4 body")
    return [md, pdf]


class TestFileEntries:
    def test_entries_carry_key_and_size(self, post, paths):
        record = build_metadata(post, URL, files=paths)
        assert record["files"]["entries"] == {
            "2026-08-28-repository-metadata.md": {
                "key": "2026-08-28-repository-metadata.md",
                "size": paths[0].stat().st_size,
            },
            "2026-08-28-repository-metadata.pdf": {
                "key": "2026-08-28-repository-metadata.pdf",
                "size": paths[1].stat().st_size,
            },
        }

    def test_files_stay_enabled(self, post, paths):
        assert build_metadata(post, URL, files=paths)["files"]["enabled"]

    def test_pdf_is_the_default_preview(self, post, paths):
        record = build_metadata(post, URL, files=paths)
        assert record["files"]["default_preview"] == (
            "2026-08-28-repository-metadata.pdf"
        )

    def test_no_pdf_means_no_default_preview(self, post, paths):
        record = build_metadata(post, URL, files=paths[:1])
        assert "default_preview" not in record["files"]

    def test_missing_file_has_a_key_but_no_size(self, post, tmp_path):
        record = build_metadata(post, URL, files=[tmp_path / "gone.pdf"])
        assert record["files"]["entries"] == {"gone.pdf": {"key": "gone.pdf"}}


class TestSourceId:
    def test_source_id_is_an_import_recid_identifier(self, post):
        record = build_metadata(
            post, URL, source_id="2026-08-28-repository-metadata"
        )
        assert {
            "identifier": "2026-08-28-repository-metadata",
            "scheme": "import-recid",
        } in record["metadata"]["identifiers"]

    def test_canonical_url_identifier_is_kept_alongside(self, post):
        record = build_metadata(post, URL, source_id="slug")
        assert {"identifier": URL, "scheme": "url"} in (
            record["metadata"]["identifiers"]
        )

    def test_no_source_id_means_no_import_recid(self, post):
        schemes = {
            i["scheme"] for i in build_metadata(post, URL)["metadata"]["identifiers"]
        }
        assert "import-recid" not in schemes
