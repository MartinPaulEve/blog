import json

import pytest

from thought_composer.mastodon import MastodonClient, MastodonError

BASE = "https://mastodon.example.org"
VERIFY_URL = f"{BASE}/api/v1/accounts/verify_credentials"
MEDIA_URL = f"{BASE}/api/v2/media"
STATUS_URL = f"{BASE}/api/v1/statuses"


class FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload
        self.text = json.dumps(payload) if payload is not None else ""

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, responses=None):
        self.responses = dict(responses or {})
        self.sent = []

    def _handle(self, method, url, **kwargs):
        self.sent.append((method, url, kwargs))
        canned = self.responses.get((method, url))
        if isinstance(canned, list):
            canned = canned.pop(0)
        return canned or FakeResponse(200, {})

    def get(self, url, **kwargs):
        return self._handle("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self._handle("POST", url, **kwargs)


def make_client(session):
    return MastodonClient(BASE, "token", session=session, sleep=lambda s: None)


def test_verify_returns_the_account_handle():
    session = FakeSession(
        {("GET", VERIFY_URL): FakeResponse(200, {"acct": "mpe"})}
    )
    assert make_client(session).verify() == "mpe"
    assert session.sent[0][2]["headers"]["Authorization"] == "Bearer token"


def test_upload_media_returns_the_id():
    session = FakeSession(
        {("POST", MEDIA_URL): FakeResponse(200, {"id": "314"})}
    )
    media_id = make_client(session).upload_media(b"png", "image/png", alt="sq")
    assert media_id == "314"
    _method, _url, kwargs = session.sent[0]
    _name, payload, mime = kwargs["files"]["file"]
    assert payload == b"png"
    assert mime == "image/png"
    assert kwargs["data"] == {"description": "sq"}


def test_upload_media_polls_while_processing():
    session = FakeSession(
        {
            ("POST", MEDIA_URL): FakeResponse(202, {"id": "314"}),
            ("GET", f"{BASE}/api/v1/media/314"): [
                FakeResponse(206, {}),
                FakeResponse(200, {"id": "314"}),
            ],
        }
    )
    assert make_client(session).upload_media(b"png", "image/png") == "314"
    polls = [s for s in session.sent if s[0] == "GET"]
    assert len(polls) == 2


def test_post_thread_chains_and_attaches_media_to_the_first():
    session = FakeSession(
        {("POST", STATUS_URL): [
            FakeResponse(200, {"id": "1", "url": f"{BASE}/@mpe/1"}),
            FakeResponse(200, {"id": "2", "url": f"{BASE}/@mpe/2"}),
        ]}
    )
    urls = make_client(session).post_thread(["one", "two"], media_ids=["314"])
    assert urls == [f"{BASE}/@mpe/1", f"{BASE}/@mpe/2"]
    payloads = [s[2]["json"] for s in session.sent]
    assert payloads[0]["status"] == "one"
    assert payloads[0]["media_ids"] == ["314"]
    assert "in_reply_to_id" not in payloads[0]
    assert payloads[1]["in_reply_to_id"] == "1"
    assert "media_ids" not in payloads[1]
    assert all(p["visibility"] == "public" for p in payloads)


def test_error_response_raises():
    session = FakeSession(
        {("POST", STATUS_URL): [FakeResponse(422, {"error": "Validation failed"})]}
    )
    with pytest.raises(MastodonError):
        make_client(session).post_thread(["hello"])
