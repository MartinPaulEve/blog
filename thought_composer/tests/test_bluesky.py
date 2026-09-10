import json

import pytest

from thought_composer.bluesky import BlueskyClient, BlueskyError

BASE = "https://pds.example.org"
SESSION_URL = f"{BASE}/xrpc/com.atproto.server.createSession"
UPLOAD_URL = f"{BASE}/xrpc/com.atproto.repo.uploadBlob"
CREATE_URL = f"{BASE}/xrpc/com.atproto.repo.createRecord"

BLOB = {"$type": "blob", "ref": {"$link": "bafyimg"}, "mimeType": "image/png", "size": 3}


class FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload
        self.text = json.dumps(payload) if payload is not None else ""

    def json(self):
        return self._payload


class FakeSession:
    """Routes (METHOD, url) to canned responses; records what was sent."""

    def __init__(self, responses=None):
        self.responses = dict(responses or {})
        self.sent = []

    def post(self, url, **kwargs):
        self.sent.append(("POST", url, kwargs))
        canned = self.responses.get(("POST", url))
        if isinstance(canned, list):
            canned = canned.pop(0)
        return canned or FakeResponse(200, {})


def logged_in(responses=None):
    responses = dict(responses or {})
    responses.setdefault(
        ("POST", SESSION_URL),
        FakeResponse(200, {"did": "did:plc:me", "accessJwt": "jwt-token"}),
    )
    session = FakeSession(responses)
    client = BlueskyClient("eve.gd", "app-pass", base_url=BASE, session=session)
    client.login()
    return client, session


def record_response(rkey, cid="bafycid"):
    return FakeResponse(
        200, {"uri": f"at://did:plc:me/app.bsky.feed.post/{rkey}", "cid": cid}
    )


def test_login_sends_credentials_and_keeps_the_did():
    client, session = logged_in()
    _method, _url, kwargs = session.sent[0]
    assert kwargs["json"] == {"identifier": "eve.gd", "password": "app-pass"}
    assert client.did == "did:plc:me"


def test_post_thread_single_segment():
    client, session = logged_in(
        {("POST", CREATE_URL): [record_response("rkey1")]}
    )
    urls = client.post_thread(["Hello world"])
    assert urls == ["https://bsky.app/profile/eve.gd/post/rkey1"]
    _method, _url, kwargs = session.sent[-1]
    record = kwargs["json"]["record"]
    assert record["text"] == "Hello world"
    assert record["$type"] == "app.bsky.feed.post"
    assert "reply" not in record
    assert kwargs["headers"]["Authorization"] == "Bearer jwt-token"


def test_post_thread_adds_link_facets_with_byte_ranges():
    client, session = logged_in(
        {("POST", CREATE_URL): [record_response("rkey1")]}
    )
    client.post_thread(["see https://example.org/x now"])
    record = session.sent[-1][2]["json"]["record"]
    (facet,) = record["facets"]
    assert facet["index"] == {"byteStart": 4, "byteEnd": 4 + len("https://example.org/x")}
    assert facet["features"] == [
        {"$type": "app.bsky.richtext.facet#link", "uri": "https://example.org/x"}
    ]


def test_post_thread_chains_replies_to_the_root():
    client, session = logged_in(
        {("POST", CREATE_URL): [
            record_response("rkey1", "cid1"),
            record_response("rkey2", "cid2"),
            record_response("rkey3", "cid3"),
        ]}
    )
    urls = client.post_thread(["one", "two", "three"])
    assert len(urls) == 3
    records = [s[2]["json"]["record"] for s in session.sent if s[1] == CREATE_URL]
    assert "reply" not in records[0]
    root = {"uri": "at://did:plc:me/app.bsky.feed.post/rkey1", "cid": "cid1"}
    assert records[1]["reply"] == {"root": root, "parent": root}
    assert records[2]["reply"]["root"] == root
    assert records[2]["reply"]["parent"]["cid"] == "cid2"


def test_images_are_uploaded_and_embedded_on_the_first_post_only():
    client, session = logged_in(
        {
            ("POST", UPLOAD_URL): FakeResponse(200, {"blob": BLOB}),
            ("POST", CREATE_URL): [
                record_response("rkey1"), record_response("rkey2"),
            ],
        }
    )
    client.post_thread(
        ["one", "two"],
        images=[{"data": b"png", "mime": "image/png", "alt": "a square"}],
    )
    upload = next(s for s in session.sent if s[1] == UPLOAD_URL)
    assert upload[2]["data"] == b"png"
    assert upload[2]["headers"]["Content-Type"] == "image/png"
    records = [s[2]["json"]["record"] for s in session.sent if s[1] == CREATE_URL]
    embed = records[0]["embed"]
    assert embed["$type"] == "app.bsky.embed.images"
    assert embed["images"] == [{"image": BLOB, "alt": "a square"}]
    assert "embed" not in records[1]


def test_link_card_is_embedded_when_no_images():
    client, session = logged_in(
        {
            ("POST", UPLOAD_URL): FakeResponse(200, {"blob": BLOB}),
            ("POST", CREATE_URL): [record_response("rkey1")],
        }
    )
    client.post_thread(
        ["see https://example.org/x"],
        card={
            "uri": "https://example.org/x",
            "title": "A page",
            "description": "About things",
            "thumb_data": b"img",
            "thumb_mime": "image/jpeg",
        },
    )
    record = session.sent[-1][2]["json"]["record"]
    external = record["embed"]["external"]
    assert record["embed"]["$type"] == "app.bsky.embed.external"
    assert external["uri"] == "https://example.org/x"
    assert external["title"] == "A page"
    assert external["thumb"] == BLOB


def test_images_win_over_the_link_card():
    client, session = logged_in(
        {
            ("POST", UPLOAD_URL): FakeResponse(200, {"blob": BLOB}),
            ("POST", CREATE_URL): [record_response("rkey1")],
        }
    )
    client.post_thread(
        ["see https://example.org/x"],
        images=[{"data": b"png", "mime": "image/png", "alt": ""}],
        card={"uri": "https://example.org/x", "title": "A page", "description": ""},
    )
    record = session.sent[-1][2]["json"]["record"]
    assert record["embed"]["$type"] == "app.bsky.embed.images"


def test_error_response_raises():
    client, _session = logged_in(
        {("POST", CREATE_URL): [FakeResponse(400, {"error": "InvalidRequest"})]}
    )
    with pytest.raises(BlueskyError):
        client.post_thread(["hello"])
