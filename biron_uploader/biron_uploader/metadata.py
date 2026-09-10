"""Building EPrints XML for a BIROn deposit of a blog post.

The field recipe mirrors the blog posts already in BIROn (e.g. eprint
57592): type article, ispublished pub, refereed FALSE, publication
eve.gd, the canonical post URL as official_url, the Rogue Scholar DOI
as id_number when present, subject CACC (School of Creative Arts,
Culture and Communication), and two CC BY 4.0 public documents — the
built PDF edition and the markdown source.
"""

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


def build_eprint_xml(post: Post, url: str) -> bytes:
    """The metadata-only EPrints XML (ep2 data 2.0) for a deposit.

    Deliberately carries no documents: BIROn's importer corrupts base64
    file payloads (it strips + and / before decoding), so attachments
    are uploaded separately as raw binary POSTs to the new eprint's
    /contents. The DOI becomes id_number when the post has one; the
    abstract is the post's first paragraph when it has one.
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

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)
