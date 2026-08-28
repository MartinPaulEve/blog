"""Building KC Works (InvenioRDM) record JSON for a blog post."""

from .posts import Post, first_paragraph

PUBLISHER = "eve.gd: Martin Paul Eve"

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


def build_metadata(post: Post, url: str, include_doi: bool = True) -> dict:
    """The full draft-record JSON body for POST /api/records.

    Includes the post DOI as an externally-managed pid when present (and
    include_doi is True), the canonical URL as a url-scheme identifier, a
    CC BY 4.0 licence, and the author's two affiliations as separate
    institutions.
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

    record = {
        "access": {"record": "public", "files": "public"},
        "files": {"enabled": True},
        "metadata": metadata,
    }
    if include_doi and post.doi:
        record["pids"] = {
            "doi": {"identifier": post.doi, "provider": "external"}
        }
    if post.tags:
        record["custom_fields"] = {"kcr:user_defined_tags": list(post.tags)}
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
