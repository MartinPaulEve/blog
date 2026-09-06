"""Building KC Works (InvenioRDM) record JSON for a blog post."""

from .posts import Post, first_paragraph

BLOG_TITLE = "eve.gd: Martin Paul Eve"
BLOG_URL = "https://eve.gd"
PUBLISHER = "Martin Paul Eve"
PUBLISHER_LOCATION = "United Kingdom"

AI_DECLARATION = (
    "All words written in this post were written by hand, by a human (the "
    "author). No generative AI was used in the production of the writing. "
    "The technical infrastructure that builds the blog and PDFs was "
    "assisted by AI coding from Claude. The full AI usage policy is "
    "available here: https://eve.gd/ai/"
)

AUTHOR = {
    "family_name": "Eve",
    "given_name": "Martin Paul",
    "kc_username": "martin_eve",
    "orcid": "0000-0002-5589-8511",
    "email": "martin.eve@bbk.ac.uk",
    "affiliations": [
        "Birkbeck, University of London",
        "Michigan State University",
    ],
}


def build_metadata(
    post: Post,
    url: str,
    include_doi: bool = True,
    pdf_filename: str | None = None,
) -> dict:
    """The full draft-record JSON body for POST /api/records.

    Includes the post DOI as an externally-managed pid when present (and
    include_doi is True), the canonical URL as a url-scheme identifier, a
    CC BY 4.0 licence, the author's two affiliations as separate
    institutions, the blog details (title, URL, publisher location), and
    the generative-AI declaration. When pdf_filename is given, that file
    becomes the record's default preview.
    """
    metadata = {
        "resource_type": {"id": "textDocument-blogPost"},
        "title": post.title,
        "publication_date": post.date,
        "publisher": PUBLISHER,
        "languages": [{"id": "eng"}],
        "creators": [_creator()],
        "rights": [{"id": "cc-by-4.0"}],
        "identifiers": [{"identifier": url, "scheme": "url"}],
    }
    description = first_paragraph(post.body)
    if description:
        metadata["description"] = description
    if post.last_modified:
        metadata["dates"] = [
            {"date": post.last_modified, "type": {"id": "updated"}}
        ]

    files = {"enabled": True}
    if pdf_filename:
        files["default_preview"] = pdf_filename

    custom_fields = {
        "journal:journal": {"title": BLOG_TITLE},
        "kcr:publication_url": BLOG_URL,
        "imprint:imprint": {"place": PUBLISHER_LOCATION},
        "kcr:ai_usage": {
            "ai_used": True,
            "ai_description": AI_DECLARATION,
        },
    }
    if post.tags:
        custom_fields["kcr:user_defined_tags"] = list(post.tags)

    record = {
        "access": {"record": "public", "files": "public"},
        "files": files,
        "metadata": metadata,
        "custom_fields": custom_fields,
    }
    if include_doi and post.doi:
        record["pids"] = {
            "doi": {"identifier": post.doi, "provider": "external"}
        }
    return record


def _creator() -> dict:
    return {
        "person_or_org": {
            "type": "personal",
            "name": f"{AUTHOR['family_name']}, {AUTHOR['given_name']}",
            "family_name": AUTHOR["family_name"],
            "given_name": AUTHOR["given_name"],
            "identifiers": [
                {"identifier": AUTHOR["kc_username"], "scheme": "kc_username"},
                {"identifier": AUTHOR["orcid"], "scheme": "orcid"},
                {"identifier": AUTHOR["email"], "scheme": "email"},
            ],
        },
        "role": {"id": "author"},
        "affiliations": [{"name": name} for name in AUTHOR["affiliations"]],
    }
