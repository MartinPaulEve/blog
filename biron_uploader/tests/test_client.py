import pytest

from biron_uploader.client import (
    BironClient,
    BironError,
    parse_deposit_receipt,
    parse_service_document,
)

BASE = "https://eprints.example.org"

SERVICE_DOCUMENT = b"""<?xml version="1.0" encoding="utf-8"?>
<service xmlns="http://www.w3.org/2007/app"
         xmlns:atom="http://www.w3.org/2005/Atom"
         xmlns:sword="http://purl.org/net/sword/">
  <sword:version>1.3</sword:version>
  <workspace>
    <atom:title>Birkbeck Institutional Research Online</atom:title>
    <collection href="https://eprints.example.org/sword-app/deposit/inbox">
      <atom:title>Repository Inbox</atom:title>
      <accept>application/zip</accept>
      <sword:acceptPackaging q="1.0">http://eprints.org/ep2/data/2.0</sword:acceptPackaging>
      <sword:acceptPackaging q="0.8">http://purl.org/net/sword-types/METSDSpaceSIP</sword:acceptPackaging>
    </collection>
    <collection href="https://eprints.example.org/sword-app/deposit/buffer">
      <atom:title>Under Review</atom:title>
      <sword:acceptPackaging q="1.0">http://eprints.org/ep2/data/2.0</sword:acceptPackaging>
    </collection>
  </workspace>
</service>
"""

DEPOSIT_ENTRY = b"""<?xml version="1.0" encoding="utf-8"?>
<atom:entry xmlns:atom="http://www.w3.org/2005/Atom"
            xmlns:sword="http://purl.org/net/sword/">
  <atom:id>https://eprints.example.org/id/eprint/58012</atom:id>
  <atom:title>A post</atom:title>
  <sword:treatment>Deposited into the inbox</sword:treatment>
</atom:entry>
"""


class FakeResponse:
    def __init__(self, status_code, body=b"", headers=None):
        self.status_code = status_code
        self.content = body
        self.text = body.decode("utf-8", "replace")
        self.headers = headers or {}


class FakeSession:
    """Routes (METHOD, url) to canned responses; records what was sent."""

    def __init__(self, responses=None):
        self.responses = dict(responses or {})
        self.sent = []

    def _handle(self, method, url, **kwargs):
        self.sent.append((method, url, kwargs))
        canned = self.responses.get((method, url))
        if isinstance(canned, list):
            response = canned.pop(0)
        else:
            response = canned
        return response or FakeResponse(200)

    def get(self, url, **kwargs):
        return self._handle("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self._handle("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self._handle("PUT", url, **kwargs)

    def delete(self, url, **kwargs):
        return self._handle("DELETE", url, **kwargs)


# --- parsers ---------------------------------------------------------------


def test_parse_service_document_lists_collections():
    collections = parse_service_document(SERVICE_DOCUMENT)
    assert collections == [
        {
            "href": "https://eprints.example.org/sword-app/deposit/inbox",
            "title": "Repository Inbox",
            "packaging": [
                "http://eprints.org/ep2/data/2.0",
                "http://purl.org/net/sword-types/METSDSpaceSIP",
            ],
        },
        {
            "href": "https://eprints.example.org/sword-app/deposit/buffer",
            "title": "Under Review",
            "packaging": ["http://eprints.org/ep2/data/2.0"],
        },
    ]


def test_parse_deposit_receipt_prefers_location_header():
    receipt = parse_deposit_receipt(
        {"Location": "https://eprints.example.org/id/eprint/59001"},
        DEPOSIT_ENTRY,
    )
    assert receipt == {
        "eprintid": 59001,
        "url": "https://eprints.example.org/id/eprint/59001/",
    }


def test_parse_deposit_receipt_falls_back_to_atom_id():
    receipt = parse_deposit_receipt({}, DEPOSIT_ENTRY)
    assert receipt == {
        "eprintid": 58012,
        "url": "https://eprints.example.org/id/eprint/58012/",
    }


def test_parse_deposit_receipt_handles_contents_location_suffix():
    # BIROn answers document creation with Location .../NNN/contents and
    # an un-namespaced <entry> body.
    receipt = parse_deposit_receipt(
        {"Location": "https://eprints.example.org/id/document/2191159/contents"},
        b"",
    )
    assert receipt == {
        "eprintid": 2191159,
        "url": "https://eprints.example.org/id/document/2191159/",
    }


def test_parse_deposit_receipt_reads_unnamespaced_entries():
    body = (
        b'<?xml version="1.0" encoding="utf-8" ?>\n<entry>\n'
        b"  <id>https://eprints.example.org/id/document/2191159</id>\n"
        b"  <title>  Text</title>\n</entry>"
    )
    receipt = parse_deposit_receipt({}, body)
    assert receipt["eprintid"] == 2191159


def test_parse_deposit_receipt_falls_back_to_body_when_location_is_odd():
    receipt = parse_deposit_receipt(
        {"Location": "https://eprints.example.org/cgi/somewhere"},
        DEPOSIT_ENTRY,
    )
    assert receipt["eprintid"] == 58012


def test_parse_deposit_receipt_without_any_id_raises():
    with pytest.raises(BironError):
        parse_deposit_receipt({}, b"<html>login page</html>")


def test_document_step_failure_names_the_created_eprint():
    create_url = f"{BASE}/id/contents"
    doc_create_url = f"{BASE}/id/eprint/58012/contents"
    session = FakeSession(
        {
            ("POST", create_url): FakeResponse(201, DEPOSIT_ENTRY),
            ("POST", doc_create_url): FakeResponse(400, b"bad document"),
        }
    )
    with pytest.raises(BironError) as exc:
        make_client(session).deposit(
            create_url,
            b"<eprints/>",
            documents=[
                {"xml": b"<documents/>", "filename": "a.pdf",
                 "mime": "application/pdf", "data": b"x"}
            ],
        )
    message = str(exc.value)
    assert "58012" in message
    assert "delete" in message.lower()


# --- client ----------------------------------------------------------------


def make_client(session, **kwargs):
    kwargs.setdefault("sleep", lambda s: None)
    return BironClient("user", "pass", base_url=BASE, session=session, **kwargs)


def test_service_document_uses_basic_auth():
    session = FakeSession(
        {("GET", f"{BASE}/sword-app/servicedocument"): FakeResponse(200, SERVICE_DOCUMENT)}
    )
    collections = make_client(session).service_document()
    assert [c["title"] for c in collections] == ["Repository Inbox", "Under Review"]
    _method, _url, kwargs = session.sent[0]
    assert kwargs["auth"] == ("user", "pass")


def test_deposit_posts_eprints_xml_package():
    url = f"{BASE}/sword-app/deposit/inbox"
    session = FakeSession({("POST", url): FakeResponse(201, DEPOSIT_ENTRY)})
    receipt = make_client(session).deposit(url, b"<eprints/>")
    assert receipt["eprintid"] == 58012
    _method, _sent_url, kwargs = session.sent[0]
    assert kwargs["data"] == b"<eprints/>"
    assert kwargs["auth"] == ("user", "pass")
    headers = kwargs["headers"]
    assert headers["X-Packaging"] == "http://eprints.org/ep2/data/2.0"
    assert headers["Content-Type"].startswith("application/xml")


def test_cookie_auth_sends_cookie_header_instead_of_basic():
    session = FakeSession(
        {("GET", f"{BASE}/sword-app/servicedocument"): FakeResponse(200, SERVICE_DOCUMENT)}
    )
    client = BironClient(
        base_url=BASE, session=session, sleep=lambda s: None,
        cookie="eprints_session=abc123",
    )
    client.service_document()
    _method, _url, kwargs = session.sent[0]
    assert kwargs["headers"]["Cookie"] == "eprints_session=abc123"
    assert kwargs.get("auth") is None


def test_client_requires_some_credential():
    with pytest.raises(ValueError):
        BironClient(base_url=BASE)


def test_deposit_to_id_contents_uses_eprints_data_content_type():
    # The CRUD endpoint keys the import plugin off the Content-Type,
    # unlike /sword-app which reads X-Packaging.
    url = f"{BASE}/id/contents"
    session = FakeSession({("POST", url): FakeResponse(201, DEPOSIT_ENTRY)})
    make_client(session).deposit(url, b"<eprints/>")
    _method, _url, kwargs = session.sent[0]
    assert kwargs["headers"]["Content-Type"].startswith(
        "application/vnd.eprints.data+xml"
    )
    # SWORD2 semantics: the deposit is complete, not a work in progress
    # to be held in the depositor's workarea.
    assert kwargs["headers"]["In-Progress"] == "false"


DOCUMENT_ENTRY = b"""<?xml version="1.0" encoding="utf-8"?>
<atom:entry xmlns:atom="http://www.w3.org/2005/Atom">
  <atom:id>https://eprints.example.org/id/document/91</atom:id>
</atom:entry>
"""


def test_deposit_creates_documents_from_xml_then_puts_raw_content():
    # BIROn's importer corrupts base64 payloads (strips + and / before
    # decoding), so each document is created from metadata XML (carrying
    # the required security field) and its bytes arrive as a raw PUT —
    # a decode-free path.
    create_url = f"{BASE}/id/contents"
    doc_create_url = f"{BASE}/id/eprint/58012/contents"
    content_url = f"{BASE}/id/document/91/contents"
    session = FakeSession(
        {
            ("POST", create_url): FakeResponse(201, DEPOSIT_ENTRY),
            ("POST", doc_create_url): FakeResponse(201, DOCUMENT_ENTRY),
            ("PUT", content_url): FakeResponse(204, b""),
        }
    )
    receipt = make_client(session).deposit(
        create_url,
        b"<eprints/>",
        documents=[
            {
                "xml": b"<documents/>",
                "filename": "post.pdf",
                "mime": "application/pdf",
                "data": b"%PDF-raw",
            }
        ],
    )
    assert receipt["eprintid"] == 58012
    doc_posts = [s for s in session.sent if s[1] == doc_create_url]
    (post_call,) = doc_posts
    assert post_call[2]["data"] == b"<documents/>"
    assert post_call[2]["headers"]["Content-Type"] == (
        "application/vnd.eprints.data+xml"
    )
    (put_call,) = [s for s in session.sent if s[1] == content_url]
    assert put_call[0] == "PUT"
    assert put_call[2]["data"] == b"%PDF-raw"
    assert put_call[2]["headers"]["Content-Type"] == "application/pdf"
    assert put_call[2]["headers"]["Content-Disposition"] == (
        'attachment; filename="post.pdf"'
    )


EPRINT_WITH_DOCS_XML = b"""<?xml version='1.0' encoding='utf-8'?>
<eprints xmlns='http://eprints.org/ep2/data/2.0'>
  <eprint id='https://eprints.example.org/id/eprint/58012'>
    <eprint_status>archive</eprint_status>
    <documents>
      <document id='https://eprints.example.org/id/document/91'>
        <docid>91</docid>
      </document>
      <document id='https://eprints.example.org/id/document/92'>
        <docid>92</docid>
      </document>
    </documents>
  </eprint>
</eprints>
"""


def test_update_replaces_metadata_and_documents_in_place():
    eprint_url = f"{BASE}/id/eprint/58012"
    session = FakeSession(
        {
            ("GET", eprint_url): FakeResponse(200, EPRINT_WITH_DOCS_XML),
            ("DELETE", f"{BASE}/id/document/91"): FakeResponse(200, b""),
            ("DELETE", f"{BASE}/id/document/92"): FakeResponse(200, b""),
            ("PUT", eprint_url): FakeResponse(200, b""),
            ("POST", f"{eprint_url}/contents"): FakeResponse(201, DOCUMENT_ENTRY),
            ("PUT", f"{BASE}/id/document/91/contents"): FakeResponse(204, b""),
        }
    )
    receipt = make_client(session).update(
        58012,
        b"<eprints/>",
        documents=[
            {
                "xml": b"<documents/>",
                "filename": "post.pdf",
                "mime": "application/pdf",
                "data": b"%PDF-new",
            }
        ],
    )
    assert receipt == {"eprintid": 58012, "url": f"{BASE}/id/eprint/58012/"}
    operations = [(s[0], s[1]) for s in session.sent]
    # old documents removed before the metadata PUT and re-attachment
    assert operations.index(("DELETE", f"{BASE}/id/document/91")) < (
        operations.index(("PUT", eprint_url))
    )
    assert ("DELETE", f"{BASE}/id/document/92") in operations
    put_call = next(s for s in session.sent if s[:2] == ("PUT", eprint_url))
    assert put_call[2]["data"] == b"<eprints/>"
    content_put = next(
        s for s in session.sent if s[1] == f"{BASE}/id/document/91/contents"
    )
    assert content_put[2]["data"] == b"%PDF-new"


def make_live_session(initial_status: bytes):
    status_xml = (
        b"<?xml version='1.0' encoding='utf-8'?>"
        b"<eprints xmlns='http://eprints.org/ep2/data/2.0'><eprint>"
        b"<eprint_status>" + initial_status + b"</eprint_status>"
        b"</eprint></eprints>"
    )
    return FakeSession(
        {
            ("POST", f"{BASE}/id/contents"): FakeResponse(201, DEPOSIT_ENTRY),
            ("GET", f"{BASE}/id/eprint/58012"): FakeResponse(200, status_xml),
            ("PUT", f"{BASE}/id/eprint/58012"): FakeResponse(200, b""),
        }
    )


def test_make_live_puts_the_record_when_not_yet_archived():
    session = make_live_session(b"inbox")
    make_client(session).deposit(
        f"{BASE}/id/contents", b"<eprints/>", make_live=True
    )
    (put_call,) = [s for s in session.sent if s[0] == "PUT"]
    assert put_call[1] == f"{BASE}/id/eprint/58012"
    assert put_call[2]["data"] == b"<eprints/>"


def test_make_live_skips_the_put_when_already_archived():
    session = make_live_session(b"archive")
    make_client(session).deposit(
        f"{BASE}/id/contents", b"<eprints/>", make_live=True
    )
    assert [s for s in session.sent if s[0] == "PUT"] == []


EPRINT_STATUS_XML = b"""<?xml version='1.0' encoding='utf-8'?>
<eprints xmlns='http://eprints.org/ep2/data/2.0'>
  <eprint><eprint_status>archive</eprint_status></eprint>
</eprints>
"""


def test_eprint_status_reads_the_record():
    session = FakeSession(
        {("GET", f"{BASE}/id/eprint/58012"): FakeResponse(200, EPRINT_STATUS_XML)}
    )
    assert make_client(session).eprint_status(58012) == "archive"


def test_eprint_status_is_none_when_unreadable():
    session = FakeSession(
        {("GET", f"{BASE}/id/eprint/58012"): FakeResponse(404, b"gone")}
    )
    assert make_client(session).eprint_status(58012) is None


def test_contents_status_reports_the_http_code_without_raising():
    session = FakeSession(
        {("GET", f"{BASE}/id/contents"): FakeResponse(401, b"denied")}
    )
    assert make_client(session).contents_status() == 401
    session = FakeSession(
        {("GET", f"{BASE}/id/contents"): FakeResponse(200, b"<feed/>")}
    )
    assert make_client(session).contents_status() == 200


def test_auth_failure_raises_with_status():
    session = FakeSession(
        {("GET", f"{BASE}/sword-app/servicedocument"): FakeResponse(401, b"denied")}
    )
    with pytest.raises(BironError) as exc:
        make_client(session).service_document()
    assert "401" in str(exc.value)


def test_transient_error_is_retried():
    url = f"{BASE}/sword-app/deposit/inbox"
    session = FakeSession(
        {("POST", url): [FakeResponse(503, b"busy"), FakeResponse(201, DEPOSIT_ENTRY)]}
    )
    receipt = make_client(session).deposit(url, b"<eprints/>")
    assert receipt["eprintid"] == 58012
    assert len(session.sent) == 2
