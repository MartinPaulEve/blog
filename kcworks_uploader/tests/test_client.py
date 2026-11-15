import json

import pytest
from kcworks_uploader.client import KCWorksClient, KCWorksConflict, KCWorksError

BASE = "https://works.example.org/api"
IMPORT_URL = f"{BASE}/import/evegd-blog-posts"


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




def imported(record_id="abc12-xyz34", files=("post.md", "post.pdf")):
    """A successful import response for one work."""
    return {
        "status": "success",
        "data": [
            {
                "item_index": 0,
                "record_id": record_id,
                "record_url": f"https://works.example.org/records/{record_id}",
                "files": {name: ["success", []] for name in files},
                "collection_id": "coll-uuid",
                "errors": [],
                "metadata": {"id": record_id},
            }
        ],
        "errors": [],
        "message": "All records were successfully imported.",
    }


@pytest.fixture
def files(tmp_path):
    md = tmp_path / "post.md"
    md.write_text("hello")
    pdf = tmp_path / "post.pdf"
    pdf.write_bytes(b"%PDF-1.4 body")
    return [md, pdf]


RECORD = {"metadata": {"title": "A post"}, "files": {"enabled": True}}


class TestImportWork:
    def run(self, files, responses=None, **kwargs):
        session = FakeSession(
            responses
            if responses is not None
            else {("POST", IMPORT_URL): FakeResponse(201, imported())}
        )
        client = KCWorksClient(
            BASE, "tok", session=session, sleep=lambda seconds: None
        )
        result = client.import_work("evegd-blog-posts", RECORD, files, **kwargs)
        return result, session

    def test_returns_the_created_work(self, files):
        result, _ = self.run(files)
        assert result["record_id"] == "abc12-xyz34"
        assert result["record_url"] == (
            "https://works.example.org/records/abc12-xyz34"
        )
        assert result["collection_id"] == "coll-uuid"
        assert set(result["files"]) == {"post.md", "post.pdf"}

    def test_posts_to_the_collection_import_endpoint(self, files):
        _, session = self.run(files)
        assert list(session.sent) == [("POST", IMPORT_URL)]

    def test_sends_bearer_token(self, files):
        session = FakeSession(
            {("POST", IMPORT_URL): FakeResponse(201, imported())}
        )
        KCWorksClient(BASE, "sekrit", session=session).import_work(
            "evegd-blog-posts", RECORD, files
        )
        assert session.headers["Authorization"] == "Bearer sekrit"

    def test_transmits_every_file_by_name_and_content(self, files):
        _, session = self.run(files)
        parts = session.sent[("POST", IMPORT_URL)]["files"]
        sent = {
            (field, part[0], part[1]) for field, part in parts
        }
        assert sent == {
            ("files", "post.md", b"hello"),
            ("files", "post.pdf", b"%PDF-1.4 body"),
        }

    def test_metadata_part_is_a_json_array_holding_the_record(self, files):
        _, session = self.run(files)
        form = session.sent[("POST", IMPORT_URL)]["data"]
        assert json.loads(form["metadata"]) == [RECORD]

    def test_review_is_not_required_by_default(self, files):
        _, session = self.run(files)
        form = session.sent[("POST", IMPORT_URL)]["data"]
        assert form["review_required"] == "false"

    def test_review_can_be_requested(self, files):
        _, session = self.run(files, review_required=True)
        form = session.sent[("POST", IMPORT_URL)]["data"]
        assert form["review_required"] == "true"

    def test_owners_are_not_emailed(self, files):
        _, session = self.run(files)
        form = session.sent[("POST", IMPORT_URL)]["data"]
        assert form["notify_record_owners"] == "false"

    def test_missing_file_is_reported_before_contacting_the_server(
        self, tmp_path
    ):
        session = FakeSession()
        client = KCWorksClient(BASE, "tok", session=session)
        with pytest.raises(FileNotFoundError):
            client.import_work(
                "evegd-blog-posts", RECORD, [tmp_path / "missing.pdf"]
            )
        assert session.sent == {}

    def test_validation_errors_surface_in_the_error(self, files):
        rejection = {
            "status": "error",
            "message": "No records were successfully imported.",
            "data": [],
            "errors": [
                {
                    "item_index": 0,
                    "record_id": None,
                    "record_url": None,
                    "errors": [
                        {"field": "title", "message": "Required field missing."}
                    ],
                    "files": {},
                    "metadata": {},
                }
            ],
        }
        with pytest.raises(KCWorksError, match="Required field missing"):
            self.run(
                files, {("POST", IMPORT_URL): FakeResponse(400, rejection)}
            )

    def test_forbidden_token_raises(self, files):
        forbidden = {
            "status": "error",
            "message": "The user does not have the necessary permissions.",
        }
        with pytest.raises(KCWorksError, match="permissions"):
            self.run(
                files, {("POST", IMPORT_URL): FakeResponse(403, forbidden)}
            )

    def test_conflict_carries_the_existing_record_location(self, files):
        existing = "https://works.example.org/records/old11-old11"
        with pytest.raises(KCWorksConflict) as info:
            self.run(
                files,
                {
                    ("POST", IMPORT_URL): FakeResponse(
                        409,
                        {"status": "error", "message": "already exists"},
                        headers={"Location": existing},
                    )
                },
            )
        assert info.value.location == existing
        assert isinstance(info.value, KCWorksError)

    def test_conflict_without_location(self, files):
        with pytest.raises(KCWorksConflict) as info:
            self.run(
                files,
                {
                    ("POST", IMPORT_URL): FakeResponse(
                        409, {"status": "error", "message": "already exists"}
                    )
                },
            )
        assert info.value.location is None

    def test_empty_success_data_is_an_error(self, files):
        with pytest.raises(KCWorksError):
            self.run(
                files,
                {
                    ("POST", IMPORT_URL): FakeResponse(
                        201, {"status": "success", "data": [], "errors": []}
                    )
                },
            )


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
    def test_import_succeeds_after_a_429(self, files):
        session = SequencedFakeSession(
            {
                ("POST", IMPORT_URL): [
                    FakeResponse(429, {"message": "rate limit exceeded"}),
                    FakeResponse(201, imported()),
                ]
            }
        )
        naps = []
        client = KCWorksClient(
            BASE, "tok", session=session, sleep=naps.append
        )
        result = client.import_work("evegd-blog-posts", RECORD, files)
        assert result["record_id"] == "abc12-xyz34"
        assert naps  # the client waited before retrying

    def test_retry_after_header_sets_the_wait(self):
        session = SequencedFakeSession(
            {
                ("GET", f"{BASE}/records/rec1"): [
                    FakeResponse(
                        429,
                        {"message": "slow down"},
                        headers={"Retry-After": "17"},
                    ),
                    FakeResponse(200, {"id": "rec1"}),
                ]
            }
        )
        naps = []
        client = KCWorksClient(
            BASE, "tok", session=session, sleep=naps.append
        )
        client.get_record("rec1")
        assert naps == [17.0]

    def test_persistent_429_raises_after_retries(self, files):
        session = SequencedFakeSession(
            {
                ("POST", IMPORT_URL): [
                    FakeResponse(429, {"message": "rate limit exceeded"})
                ]
            }
        )
        client = KCWorksClient(
            BASE, "tok", session=session, sleep=lambda seconds: None
        )
        with pytest.raises(KCWorksError, match="429"):
            client.import_work("evegd-blog-posts", RECORD, files)

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
            {("GET", f"{BASE}/records/rec1"): FakeResponse(200, {"id": "rec1"})}
        )
        naps = []
        client = KCWorksClient(
            BASE, "tok", session=session, sleep=naps.append
        )
        client.get_record("rec1")
        assert naps == []

    def test_client_errors_are_not_retried(self, files):
        session = SequencedFakeSession(
            {
                ("POST", IMPORT_URL): [
                    FakeResponse(400, {"message": "validation error"}),
                    FakeResponse(201, imported()),
                ]
            }
        )
        client = KCWorksClient(
            BASE, "tok", session=session, sleep=lambda seconds: None
        )
        with pytest.raises(KCWorksError, match="validation error"):
            client.import_work("evegd-blog-posts", RECORD, files)


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




class TestRequestLog:
    """A ``log`` callable receives a line per request and per retry."""

    def test_default_client_logs_nothing_and_works(self, files):
        session = FakeSession(
            {("POST", IMPORT_URL): FakeResponse(201, imported())}
        )
        client = KCWorksClient(BASE, "tok", session=session)
        assert client.import_work("evegd-blog-posts", RECORD, files)

    def test_successful_request_logs_the_post_and_its_status(self, files):
        lines = []
        session = FakeSession(
            {("POST", IMPORT_URL): FakeResponse(201, imported())}
        )
        client = KCWorksClient(BASE, "tok", session=session, log=lines.append)
        client.import_work("evegd-blog-posts", RECORD, files)
        assert any("POST" in line and IMPORT_URL in line for line in lines)
        assert any("201" in line for line in lines)
        assert not any("retried" in line.lower() for line in lines)

    def test_retry_is_logged_with_the_error_and_the_wait(self, files):
        lines = []
        session = SequencedFakeSession(
            {
                ("POST", IMPORT_URL): [
                    FakeResponse(
                        429,
                        {"message": "rate limit exceeded"},
                        headers={"Retry-After": "5"},
                    ),
                    FakeResponse(201, imported()),
                ]
            }
        )
        client = KCWorksClient(
            BASE, "tok", session=session, sleep=lambda s: None, log=lines.append
        )
        client.import_work("evegd-blog-posts", RECORD, files)
        retry = [line for line in lines if "retried" in line.lower()]
        assert len(retry) == 1
        assert IMPORT_URL in retry[0]
        assert "429" in retry[0] and "rate limit exceeded" in retry[0]
        assert "5" in retry[0]
        assert lines.index(retry[0]) < len(lines) - 1  # the retry follows

    def test_final_failure_is_logged_without_a_retry_promise(self, files):
        lines = []
        session = SequencedFakeSession(
            {("POST", IMPORT_URL): [FakeResponse(503, {"message": "down"})]}
        )
        client = KCWorksClient(
            BASE, "tok", session=session, sleep=lambda s: None, log=lines.append
        )
        with pytest.raises(KCWorksError):
            client.import_work("evegd-blog-posts", RECORD, files)
        assert "503" in lines[-1] and "down" in lines[-1]
        assert "retried" not in lines[-1].lower()

    def test_rejections_are_logged(self, files):
        lines = []
        session = FakeSession(
            {("POST", IMPORT_URL): FakeResponse(403, {"message": "no perms"})}
        )
        client = KCWorksClient(BASE, "tok", session=session, log=lines.append)
        with pytest.raises(KCWorksError):
            client.import_work("evegd-blog-posts", RECORD, files)
        assert any("403" in line and "no perms" in line for line in lines)

    def test_files_being_sent_are_logged(self, files):
        lines = []
        session = FakeSession(
            {("POST", IMPORT_URL): FakeResponse(201, imported())}
        )
        client = KCWorksClient(BASE, "tok", session=session, log=lines.append)
        client.import_work("evegd-blog-posts", RECORD, files)
        assert any("post.pdf" in line for line in lines)


class TestRequestLogDetail:
    """The trace carries enough to diagnose a failure: headers both
    ways, the form fields and JSON sent, the files attached, and the
    response body."""

    TOKEN = "sekrit-token-123"

    def run(self, files, response=None, **kwargs):
        lines = []
        session = FakeSession(
            {
                ("POST", IMPORT_URL): response
                or FakeResponse(
                    201,
                    imported(),
                    headers={
                        "Content-Type": "application/json",
                        "X-Request-Id": "req-9",
                    },
                )
            }
        )
        client = KCWorksClient(
            BASE,
            self.TOKEN,
            session=session,
            sleep=lambda s: None,
            log=lines.append,
            **kwargs,
        )
        try:
            client.import_work("evegd-blog-posts", RECORD, files)
        except KCWorksError:
            pass
        return "\n".join(lines)

    def test_request_headers_are_logged_with_the_token_redacted(self, files):
        trace = self.run(files)
        assert "Accept: application/json" in trace
        assert "Authorization: Bearer" in trace
        assert self.TOKEN not in trace

    def test_form_fields_are_logged(self, files):
        trace = self.run(files)
        assert "review_required: false" in trace
        assert "notify_record_owners: false" in trace

    def test_submitted_json_is_logged_in_full(self, files):
        trace = self.run(files)
        assert '"title": "A post"' in trace
        assert '"enabled": true' in trace

    def test_attached_files_are_logged_with_size_and_type(self, files):
        trace = self.run(files)
        assert "post.pdf" in trace
        assert str(len(b"%PDF-1.4 body")) in trace
        assert "application/octet-stream" in trace

    def test_response_headers_are_logged(self, files):
        trace = self.run(files)
        assert "X-Request-Id: req-9" in trace

    def test_response_body_is_logged(self, files):
        trace = self.run(files)
        assert "https://works.example.org/records/abc12-xyz34" in trace

    def test_non_json_response_body_is_logged_as_text(self, files):
        gateway = FakeResponse(502, None)
        gateway.text = "<html><body>502 Bad Gateway</body></html>"
        trace = self.run(files, response=gateway, max_retries=0)
        assert "502 Bad Gateway" in trace

    def test_json_bodies_are_logged_for_plain_requests(self):
        lines = []
        session = FakeSession(
            {
                (
                    "POST",
                    f"{BASE}/records/rec1/communities",
                ): FakeResponse(200, {"processed": []})
            }
        )
        client = KCWorksClient(BASE, "tok", session=session, log=lines.append)
        client.add_to_collection("rec1", "coll-uuid")
        trace = "\n".join(lines)
        assert '"id": "coll-uuid"' in trace
        assert '"processed": []' in trace

    def test_nothing_is_built_without_a_logger(self, files):
        session = FakeSession(
            {("POST", IMPORT_URL): FakeResponse(201, imported())}
        )
        client = KCWorksClient(BASE, "tok", session=session)
        assert client.import_work("evegd-blog-posts", RECORD, files)

    def test_request_detail_is_shown_once_across_retries(self, files):
        lines = []
        session = SequencedFakeSession(
            {
                ("POST", IMPORT_URL): [
                    FakeResponse(429, {"message": "slow down"}),
                    FakeResponse(201, imported()),
                ]
            }
        )
        client = KCWorksClient(
            BASE, "tok", session=session, sleep=lambda s: None, log=lines.append
        )
        client.import_work("evegd-blog-posts", RECORD, files)
        trace = "\n".join(lines)
        assert trace.count('"title": "A post"') == 1
        assert trace.count("Request headers:") == 1
        posts = [line for line in lines if line.startswith("POSTing to")]
        assert len(posts) == 2
        assert "retry 1 of" in posts[1]

    def test_response_cookies_are_redacted(self, files):
        trace = self.run(
            files,
            response=FakeResponse(
                201,
                imported(),
                headers={"Set-Cookie": "csrftoken=verysecretvalue; Path=/"},
            ),
        )
        assert "Set-Cookie" in trace
        assert "verysecretvalue" not in trace
