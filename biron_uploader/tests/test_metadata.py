import base64
import xml.etree.ElementTree as ET
from pathlib import Path

from biron_uploader.metadata import EP2_NS, build_eprint_xml
from kcworks_uploader.posts import Post

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


def build_tree(post, files=None):
    files = files if files is not None else [
        ("a-post.pdf", "application/pdf", b"%PDF-fake"),
        ("2026-08-28-a-post.md", "text/plain", b"markdown source"),
    ]
    xml = build_eprint_xml(post, URL, files)
    return ET.fromstring(xml)


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


def test_documents_embed_files_base64():
    pdf_bytes = b"%PDF-fake-bytes"
    tree = build_tree(
        make_post(),
        files=[
            ("a-post.pdf", "application/pdf", pdf_bytes),
            ("2026-08-28-a-post.md", "text/plain", b"body"),
        ],
    )
    docs = tree.findall(f".//{{{EP2_NS}}}documents/{{{EP2_NS}}}document")
    assert len(docs) == 2
    pdf_doc = docs[0]
    assert pdf_doc.find(f"{{{EP2_NS}}}license").text == "cc_by_4"
    assert pdf_doc.find(f"{{{EP2_NS}}}security").text == "public"
    assert pdf_doc.find(f"{{{EP2_NS}}}content").text == "published"
    assert pdf_doc.find(f"{{{EP2_NS}}}language").text == "en"
    assert pdf_doc.find(f"{{{EP2_NS}}}main").text == "a-post.pdf"
    assert pdf_doc.find(f"{{{EP2_NS}}}mime_type").text == "application/pdf"
    file_el = pdf_doc.find(f".//{{{EP2_NS}}}file")
    assert file_el.find(f"{{{EP2_NS}}}filename").text == "a-post.pdf"
    data = file_el.find(f"{{{EP2_NS}}}data")
    assert data.get("encoding") == "base64"
    assert base64.b64decode(data.text) == pdf_bytes


def test_no_abstract_element_when_body_is_empty():
    tree = build_tree(make_post(body=""))
    assert tree.find(f".//{{{EP2_NS}}}abstract") is None


def test_output_is_valid_utf8_xml_bytes():
    xml = build_eprint_xml(
        make_post(title="Adorno terminology: άλλο γένος"),
        URL,
        [("f.md", "text/plain", b"x")],
    )
    assert isinstance(xml, bytes)
    tree = ET.fromstring(xml)
    assert "άλλο γένος" in tree.find(f".//{{{EP2_NS}}}title").text
