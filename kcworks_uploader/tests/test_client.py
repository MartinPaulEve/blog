import pytest
from kcworks_uploader.client import KCWorksClient, KCWorksError

BASE = "https://works.example.org/api"


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

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
        client = KCWorksClient(BASE, "tok", session=session)
        with pytest.raises(KCWorksError, match="boom"):
            client.upload_files("abc", [md])
