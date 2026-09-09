"""Building EPrints XML for a BIROn deposit of a blog post.

The field recipe mirrors the blog posts already in BIROn (e.g. eprint
57592): type article, ispublished pub, refereed FALSE, publication
eve.gd, the canonical post URL as official_url, the Rogue Scholar DOI
as id_number when present, subject CACC (School of Creative Arts,
Culture and Communication), and two CC BY 4.0 public documents — the
built PDF edition and the markdown source.
"""

import base64
import xml.etree.ElementTree as ET

from kcworks_uploader.posts import Post, first_paragraph

EP2_NS = "http://eprints.org/ep2/data/2.0"
SUBJECT = "CACC"
CREATOR = {"family": "Eve", "given": "Martin Paul", "staffid": "ubmeve001"}


def _el(parent, name, text=None):
    el = ET.SubElement(parent, f"{{{EP2_NS}}}{name}")
    if text is not None:
        el.text = text
    return el


def build_eprint_xml(
    post: Post,
    url: str,
    files: list[tuple[str, str, bytes]],
) -> bytes:
    """The EPrints XML (ep2 data 2.0) payload for a SWORD deposit.

    ``files`` is a list of (filename, mime_type, content) attachments;
    each becomes its own public, published, CC BY 4.0 document with the
    file embedded base64. The DOI becomes id_number when the post has
    one; the abstract is the post's first paragraph when it has one.
    """
    ET.register_namespace("", EP2_NS)
    root = ET.Element(f"{{{EP2_NS}}}eprints")
    ep = ET.SubElement(root, f"{{{EP2_NS}}}eprint")

    _el(ep, "type", "article")
    _el(ep, "title", post.title)
    abstract = first_paragraph(post.body)
    if abstract:
        _el(ep, "abstract", abstract)

    item = _el(_el(ep, "creators"), "item")
    name = _el(item, "name")
    _el(name, "family", CREATOR["family"])
    _el(name, "given", CREATOR["given"])
    _el(item, "staffid", CREATOR["staffid"])
    _el(_el(ep, "subjects"), "item", SUBJECT)

    _el(ep, "date", post.date)
    _el(ep, "date_type", "published")
    _el(ep, "ispublished", "pub")
    _el(ep, "refereed", "FALSE")
    _el(ep, "publication", "eve.gd")
    _el(ep, "official_url", url)
    if post.doi:
        _el(ep, "id_number", post.doi)
    _el(ep, "oa_status", "gold")
    _el(ep, "full_text_status", "public")

    documents = _el(ep, "documents")
    for placement, (filename, mime_type, content) in enumerate(files, 1):
        doc = _el(documents, "document")
        _el(doc, "language", "en")
        _el(doc, "placement", str(placement))
        _el(doc, "format", "text")
        _el(doc, "license", "cc_by_4")
        _el(doc, "content", "published")
        _el(doc, "security", "public")
        _el(doc, "main", filename)
        _el(doc, "mime_type", mime_type)
        file_el = _el(_el(doc, "files"), "file")
        _el(file_el, "filename", filename)
        _el(file_el, "mime_type", mime_type)
        data = _el(file_el, "data", base64.b64encode(content).decode("ascii"))
        data.set("encoding", "base64")

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)
