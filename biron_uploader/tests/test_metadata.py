import xml.etree.ElementTree as ET
from pathlib import Path

from kcworks_uploader.posts import Post

from biron_uploader.metadata import EP2_NS, build_eprint_xml

URL = "https://eve.gd/2026/08/28/a-post/"


def make_post(**overrides):
    fields = {
        "path": Path("_posts/2026-08-28-a-post.md"),
        "title": "A post about things & stuff",
        "date": "2026-08-28",
        "doi": "10.59348/mjvdw-w0051",
        "body": "First paragraph of the post.\n\nSecond paragraph.\n",
    }
    fields.update(overrides)
    return Post(**fields)


def build_tree(post):
    return ET.fromstring(build_eprint_xml(post, URL))


def field(tree, name):
    el = tree.find(f".//{{{EP2_NS}}}{name}")
    return None if el is None else el.text


def test_root_is_ep2_eprints_with_one_eprint():
    tree = build_tree(make_post())
    assert tree.tag == f"{{{EP2_NS}}}eprints"
    assert len(tree.findall(f"{{{EP2_NS}}}eprint")) == 1


def test_core_fields_match_existing_blog_deposits():
    tree = build_tree(make_post())
    assert field(tree, "type") == "article"
    assert field(tree, "ispublished") == "pub"
    assert field(tree, "refereed") == "FALSE"
    assert field(tree, "publication") == "eve.gd"
    assert field(tree, "official_url") == URL
    assert field(tree, "oa_status") == "gold"
    assert field(tree, "full_text_status") == "public"
    assert field(tree, "date") == "2026-08-28"
    assert field(tree, "date_type") == "published"


def test_title_and_abstract():
    tree = build_tree(make_post())
    assert field(tree, "title") == "A post about things & stuff"
    assert field(tree, "abstract") == "First paragraph of the post."


def test_creator_and_subject():
    tree = build_tree(make_post())
    creator = tree.find(
        f".//{{{EP2_NS}}}creators/{{{EP2_NS}}}item"
    )
    assert creator.find(f"{{{EP2_NS}}}name/{{{EP2_NS}}}family").text == "Eve"
    assert (
        creator.find(f"{{{EP2_NS}}}name/{{{EP2_NS}}}given").text
        == "Martin Paul"
    )
    assert creator.find(f"{{{EP2_NS}}}staffid").text == "ubmeve001"
    subject = tree.find(f".//{{{EP2_NS}}}subjects/{{{EP2_NS}}}item")
    assert subject.text == "CACC"


def test_doi_becomes_id_number_when_present_only():
    assert field(build_tree(make_post()), "id_number") == "10.59348/mjvdw-w0051"
    tree = build_tree(make_post(doi=None))
    assert tree.find(f".//{{{EP2_NS}}}id_number") is None


def test_no_documents_are_embedded_in_the_metadata():
    # BIROn's importer corrupts base64 file payloads (it strips + and /
    # before decoding), so files travel as separate raw uploads and the
    # record XML must stay metadata-only.
    tree = build_tree(make_post())
    assert tree.find(f".//{{{EP2_NS}}}documents") is None
    assert tree.find(f".//{{{EP2_NS}}}data") is None


def test_no_abstract_element_when_body_is_empty():
    tree = build_tree(make_post(body=""))
    assert tree.find(f".//{{{EP2_NS}}}abstract") is None


def test_output_is_valid_utf8_xml_bytes():
    xml = build_eprint_xml(
        make_post(title="Adorno terminology: άλλο γένος"), URL
    )
    assert isinstance(xml, bytes)
    tree = ET.fromstring(xml)
    assert "άλλο γένος" in tree.find(f".//{{{EP2_NS}}}title").text
