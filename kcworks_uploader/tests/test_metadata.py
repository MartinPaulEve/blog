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

    def test_pdf_filename_becomes_default_preview(self, post):
        record = build_metadata(post, URL, pdf_filename="post.pdf")
        assert record["files"] == {
            "enabled": True,
            "default_preview": "post.pdf",
        }


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
