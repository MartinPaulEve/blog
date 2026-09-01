import pytest

from kcworks_uploader.client import KCWorksClient, KCWorksError

BASE = "https://works.example.org/api"


class FakeResponse:
    def __init__(self, status_code, payload, headers=None):
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)
        self.headers = headers or {}

    def json(self):
        if self._payload is None:
            raise ValueError("no JSON")
        return self._payload


class FakeSession:
    """An in-memory stand-in for requests.Session.

    Routes (METHOD, url) to canned responses and keeps what was sent so
    tests can assert on the transmitted data. Unrouted requests succeed
    with an empty JSON object.
    """

    def __init__(self, responses=None):
        self.headers = {}
        self.sent = {}
        self.responses = responses or {}

    def _handle(self, method, url, **kwargs):
        data = kwargs.get("data")
        if hasattr(data, "read"):
            kwargs["data"] = data.read()
        self.sent[(method, url)] = kwargs
        return self.responses.get((method, url), FakeResponse(200, {}))

    def post(self, url, **kwargs):
        return self._handle("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self._handle("PUT", url, **kwargs)

    def get(self, url, **kwargs):
        return self._handle("GET", url, **kwargs)


class TestCreateDraft:
    def test_returns_created_draft_json(self):
        draft = {"id": "abc12-xyz34", "links": {"self": "..."}}
        session = FakeSession(
            {("POST", f"{BASE}/records"): FakeResponse(201, draft)}
        )
        client = KCWorksClient(BASE, "tok", session=session)
        assert client.create_draft({"metadata": {}}) == draft

    def test_sends_bearer_token(self):
        session = FakeSession(
            {("POST", f"{BASE}/records"): FakeResponse(201, {"id": "x"})}
        )
        KCWorksClient(BASE, "sekrit", session=session).create_draft({})
        assert session.headers["Authorization"] == "Bearer sekrit"

    def test_server_rejection_raises_kcworks_error(self):
        session = FakeSession(
            {
                ("POST", f"{BASE}/records"): FakeResponse(
                    400, {"message": "A validation error occurred."}
                )
            }
        )
        client = KCWorksClient(BASE, "tok", session=session)
        with pytest.raises(KCWorksError, match="validation error"):
            client.create_draft({})


class TestUpdateDraft:
    def test_returns_updated_draft_json(self):
        updated = {"id": "abc", "files": {"default_preview": "post.pdf"}}
        session = FakeSession(
            {("PUT", f"{BASE}/records/abc/draft"): FakeResponse(200, updated)}
        )
        client = KCWorksClient(BASE, "tok", session=session)
        assert client.update_draft("abc", {"metadata": {}}) == updated

    def test_server_rejection_raises_kcworks_error(self):
        session = FakeSession(
            {
                ("PUT", f"{BASE}/records/abc/draft"): FakeResponse(
                    400, {"message": "bad update"}
                )
            }
        )
        client = KCWorksClient(BASE, "tok", session=session)
        with pytest.raises(KCWorksError, match="bad update"):
            client.update_draft("abc", {})


class TestPublishDraft:
    def test_returns_published_record_json(self):
        published = {"id": "abc", "links": {"self_html": "..."}}
        session = FakeSession(
            {
                (
                    "POST",
                    f"{BASE}/records/abc/draft/actions/publish",
                ): FakeResponse(202, published)
            }
        )
        client = KCWorksClient(BASE, "tok", session=session)
        assert client.publish_draft("abc") == published

    def test_server_rejection_raises_kcworks_error(self):
        session = FakeSession(
            {
                (
                    "POST",
                    f"{BASE}/records/abc/draft/actions/publish",
                ): FakeResponse(400, {"message": "cannot publish"})
            }
        )
        client = KCWorksClient(BASE, "tok", session=session)
        with pytest.raises(KCWorksError, match="cannot publish"):
            client.publish_draft("abc")


class TestUploadFiles:
    def test_returns_committed_file_keys(self, tmp_path):
        md = tmp_path / "post.md"
        md.write_text("hello")
        pdf = tmp_path / "post.pdf"
        pdf.write_bytes(b"%PDF-1.4")
        client = KCWorksClient(BASE, "tok", session=FakeSession())
        assert client.upload_files("abc", [md, pdf]) == [
            "post.md",
            "post.pdf",
        ]

    def test_transmits_file_contents(self, tmp_path):
        pdf = tmp_path / "post.pdf"
        pdf.write_bytes(b"%PDF-1.4 body")
        session = FakeSession()
        client = KCWorksClient(BASE, "tok", session=session)
        client.upload_files("abc", [pdf])
        sent = session.sent[
            ("PUT", f"{BASE}/records/abc/draft/files/post.pdf/content")
        ]
        assert sent["data"] == b"%PDF-1.4 body"

    def test_failed_commit_raises_kcworks_error(self, tmp_path):
        md = tmp_path / "post.md"
        md.write_text("hello")
        session = FakeSession(
            {
                (
                    "POST",
                    f"{BASE}/records/abc/draft/files/post.md/commit",
                ): FakeResponse(500, {"message": "boom"})
            }
        )
        client = KCWorksClient(
            BASE, "tok", session=session, sleep=lambda seconds: None
        )
        with pytest.raises(KCWorksError, match="boom"):
            client.upload_files("abc", [md])


class SequencedFakeSession(FakeSession):
    """FakeSession whose routed responses are lists consumed in order.

    The last response in a list keeps answering once the sequence is
    exhausted, so retries beyond the scripted run see a stable server.
    """

    def _handle(self, method, url, **kwargs):
        sequence = self.responses.get((method, url))
        if isinstance(sequence, list):
            response = sequence.pop(0) if len(sequence) > 1 else sequence[0]
            self.sent[(method, url)] = kwargs
            return response
        return super()._handle(method, url, **kwargs)


class TestRateLimitRetries:
    def test_request_succeeds_after_a_429(self):
        draft = {"id": "abc12-xyz34"}
        session = SequencedFakeSession(
            {
                ("POST", f"{BASE}/records"): [
                    FakeResponse(429, {"message": "rate limit exceeded"}),
                    FakeResponse(201, draft),
                ]
            }
        )
        naps = []
        client = KCWorksClient(
            BASE, "tok", session=session, sleep=naps.append
        )
        assert client.create_draft({"metadata": {}}) == draft
        assert naps  # the client waited before retrying

    def test_retry_after_header_sets_the_wait(self):
        session = SequencedFakeSession(
            {
                ("POST", f"{BASE}/records"): [
                    FakeResponse(
                        429,
                        {"message": "slow down"},
                        headers={"Retry-After": "17"},
                    ),
                    FakeResponse(201, {"id": "x"}),
                ]
            }
        )
        naps = []
        client = KCWorksClient(
            BASE, "tok", session=session, sleep=naps.append
        )
        client.create_draft({})
        assert naps == [17.0]

    def test_persistent_429_raises_after_retries(self):
        session = SequencedFakeSession(
            {
                ("POST", f"{BASE}/records"): [
                    FakeResponse(429, {"message": "rate limit exceeded"})
                ]
            }
        )
        client = KCWorksClient(
            BASE, "tok", session=session, sleep=lambda seconds: None
        )
        with pytest.raises(KCWorksError, match="429"):
            client.create_draft({})

    def test_transient_503_is_retried(self):
        session = SequencedFakeSession(
            {
                ("GET", f"{BASE}/records/rec1"): [
                    FakeResponse(503, {"message": "maintenance"}),
                    FakeResponse(200, {"id": "rec1"}),
                ]
            }
        )
        client = KCWorksClient(
            BASE, "tok", session=session, sleep=lambda seconds: None
        )
        assert client.get_record("rec1") == {"id": "rec1"}

    def test_successful_request_never_waits(self):
        session = FakeSession(
            {("POST", f"{BASE}/records"): FakeResponse(201, {"id": "x"})}
        )
        naps = []
        client = KCWorksClient(
            BASE, "tok", session=session, sleep=naps.append
        )
        client.create_draft({})
        assert naps == []

    def test_client_errors_are_not_retried(self):
        session = SequencedFakeSession(
            {
                ("POST", f"{BASE}/records"): [
                    FakeResponse(400, {"message": "validation error"}),
                    FakeResponse(201, {"id": "should-not-be-reached"}),
                ]
            }
        )
        client = KCWorksClient(
            BASE, "tok", session=session, sleep=lambda seconds: None
        )
        with pytest.raises(KCWorksError, match="validation error"):
            client.create_draft({})


class TestCollections:
    def test_add_to_collection_posts_the_community_id(self):
        session = FakeSession(
            {
                ("POST", f"{BASE}/records/rec1/communities"): FakeResponse(
                    200, {"processed": [{"request_id": "req1"}]}
                )
            }
        )
        client = KCWorksClient(BASE, "tok", session=session)
        result = client.add_to_collection("rec1", "coll-uuid")
        assert result == {"processed": [{"request_id": "req1"}]}
        sent = session.sent[("POST", f"{BASE}/records/rec1/communities")]
        assert sent["json"] == {"communities": [{"id": "coll-uuid"}]}

    def test_accept_request_posts_the_accept_action(self):
        session = FakeSession(
            {
                (
                    "POST",
                    f"{BASE}/requests/req1/actions/accept",
                ): FakeResponse(200, {"status": "accepted"})
            }
        )
        client = KCWorksClient(BASE, "tok", session=session)
        assert client.accept_request("req1") == {"status": "accepted"}

    def test_create_collection_posts_to_communities(self):
        payload = {"slug": "s", "metadata": {"title": "T"}}
        session = FakeSession(
            {
                ("POST", f"{BASE}/communities"): FakeResponse(
                    201, {"id": "uuid-1", "slug": "s"}
                )
            }
        )
        client = KCWorksClient(BASE, "tok", session=session)
        assert client.create_collection(payload) == {
            "id": "uuid-1",
            "slug": "s",
        }
        assert session.sent[("POST", f"{BASE}/communities")]["json"] == payload

    def test_get_collection_by_slug(self):
        session = FakeSession(
            {
                ("GET", f"{BASE}/communities/s"): FakeResponse(
                    200, {"id": "uuid-1", "slug": "s"}
                )
            }
        )
        client = KCWorksClient(BASE, "tok", session=session)
        assert client.get_collection("s")["id"] == "uuid-1"

    def test_get_record_by_id(self):
        session = FakeSession(
            {
                ("GET", f"{BASE}/records/rec1"): FakeResponse(
                    200, {"id": "rec1", "parent": {}}
                )
            }
        )
        client = KCWorksClient(BASE, "tok", session=session)
        assert client.get_record("rec1")["id"] == "rec1"

    def test_error_status_raises(self):
        session = FakeSession(
            {
                ("POST", f"{BASE}/records/rec1/communities"): FakeResponse(
                    403, {"message": "Permission denied"}
                )
            }
        )
        client = KCWorksClient(BASE, "tok", session=session)
        with pytest.raises(KCWorksError, match="403"):
            client.add_to_collection("rec1", "c")


class TestUploadCollectionLogo:
    def test_puts_the_image_bytes(self, tmp_path):
        logo = tmp_path / "icon.png"
        logo.write_bytes(b"\x89PNG fake image bytes")
        session = FakeSession(
            {
                ("PUT", f"{BASE}/communities/uuid-1/logo"): FakeResponse(
                    200, {"size": 21}
                )
            }
        )
        client = KCWorksClient(BASE, "tok", session=session)
        assert client.upload_collection_logo("uuid-1", logo) == {"size": 21}
        sent = session.sent[("PUT", f"{BASE}/communities/uuid-1/logo")]
        assert sent["data"] == b"\x89PNG fake image bytes"
        assert sent["headers"]["Content-Type"] == "application/octet-stream"
