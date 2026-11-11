"""A minimal KC Works (InvenioRDM) API client.

Deposits go through the streamlined import API, which creates, attaches
files to, publishes and collects a work in one request. The ordinary
records and communities endpoints are kept only for what the import API
has no equivalent of: publishing a hand-made draft, reading a record,
and managing the blog's collection.
"""

import json
import time
from pathlib import Path

import requests

RETRY_STATUSES = {429, 500, 502, 503, 504}
IMPORT_TIMEOUT = (30, 900)  # connect, read: a PDF upload can take a while


class KCWorksError(RuntimeError):
    """An API request that the KC Works server rejected."""


class KCWorksConflict(KCWorksError):
    """An import the server refused because the work already exists
    (HTTP 409); ``location`` is the existing record's URL when given."""

    def __init__(self, message: str, location: str | None = None):
        super().__init__(message)
        self.location = location


class KCWorksClient:
    """Talks to the KC Works API with a bearer token.

    Rate limiting (429) and transient server errors (5xx) are retried
    with a backoff wait — honouring the Retry-After header when the
    server sends one — before an error is finally raised.
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        session=None,
        max_retries: int = 4,
        sleep=time.sleep,
    ):
        self.base_url = base_url.rstrip("/")
        self._session = session if session is not None else requests.Session()
        self._session.headers["Authorization"] = f"Bearer {token}"
        self._max_retries = max_retries
        self._sleep = sleep

    def _request(self, method: str, url: str, **kwargs):
        """Issue a request, retrying rate limits and transient errors;
        return the final response unexamined."""
        for attempt in range(self._max_retries + 1):
            response = getattr(self._session, method)(url, **kwargs)
            if (
                response.status_code not in RETRY_STATUSES
                or attempt == self._max_retries
            ):
                return response
            self._sleep(_retry_delay(response, attempt))
        raise AssertionError("unreachable")

    def _send(self, method: str, url: str, **kwargs) -> dict:
        """Issue a request and return its JSON, raising on rejection."""
        return self._checked(self._request(method, url, **kwargs))

    def import_work(
        self,
        collection: str,
        record: dict,
        paths: list[Path],
        review_required: bool = False,
    ) -> dict:
        """POST a work and its files to the streamlined import API.

        One multipart request to /import/{collection} creates the record,
        attaches every file, publishes it and places it in the collection
        (bypassing review unless review_required). Returns the work's
        entry from the response's data array: record_id, record_url,
        files, collection_id, errors and the full metadata.

        File contents are sent as bytes so a rate-limited request can be
        retried safely. A 409 raises KCWorksConflict carrying the
        existing work's Location, when the server gives one.
        """
        paths = [Path(path) for path in paths]
        for path in paths:
            if not path.is_file():
                raise FileNotFoundError(f"No such file to import: {path}")
        parts = [
            ("files", (path.name, path.read_bytes(), "application/octet-stream"))
            for path in paths
        ]
        form = {
            "metadata": json.dumps([record]),
            "review_required": "true" if review_required else "false",
            "notify_record_owners": "false",
        }
        response = self._request(
            "post",
            f"{self.base_url}/import/{collection}",
            files=parts,
            data=form,
            headers={"Accept": "application/json"},
            timeout=IMPORT_TIMEOUT,
        )
        if response.status_code == 409:
            raise KCWorksConflict(
                f"KC Works returned HTTP 409: {_detail(response)}",
                location=response.headers.get("Location"),
            )
        payload = self._checked(response)
        works = payload.get("data") or []
        if not works:
            raise KCWorksError(
                "KC Works import returned no work: "
                f"{payload.get('message') or payload}"
            )
        return works[0]

    def publish_draft(self, draft_id: str) -> dict:
        """POST the publish action for a draft; return the published record."""
        return self._send(
            "post",
            f"{self.base_url}/records/{draft_id}/draft/actions/publish",
        )

    @staticmethod
    def _checked(response) -> dict:
        if response.status_code not in (200, 201, 202, 204):
            raise KCWorksError(
                f"KC Works returned HTTP {response.status_code}: "
                f"{_detail(response)}"
            )
        try:
            return response.json()
        except ValueError:
            return {}

    def get_record(self, record_id: str) -> dict:
        """GET a published record's JSON."""
        return self._send("get", f"{self.base_url}/records/{record_id}")

    def add_to_collection(self, record_id: str, collection_id: str) -> dict:
        """Ask for a published record's inclusion in a collection."""
        return self._send(
            "post",
            f"{self.base_url}/records/{record_id}/communities",
            json={"communities": [{"id": collection_id}]},
        )

    def accept_request(self, request_id: str) -> dict:
        """Accept a pending request (e.g. a collection inclusion)."""
        return self._send(
            "post", f"{self.base_url}/requests/{request_id}/actions/accept"
        )

    def create_collection(self, payload: dict) -> dict:
        """POST a new collection (community); return its JSON."""
        return self._send(
            "post", f"{self.base_url}/communities", json=payload
        )

    def get_collection(self, slug: str) -> dict:
        """GET a collection's JSON by slug or id."""
        return self._send("get", f"{self.base_url}/communities/{slug}")

    def upload_collection_logo(self, collection_id: str, path: Path) -> dict:
        """PUT an image as a collection's logo."""
        return self._send(
            "put",
            f"{self.base_url}/communities/{collection_id}/logo",
            data=Path(path).read_bytes(),
            headers={"Content-Type": "application/octet-stream"},
        )


def _detail(response) -> str:
    """A readable account of an error response: its message plus any
    per-work or per-field errors it lists."""
    try:
        payload = response.json()
    except ValueError:
        return response.text
    if not isinstance(payload, dict):
        return str(payload)
    detail = str(payload.get("message") or payload)
    problems = _flatten_errors(payload.get("errors") or [])
    if problems:
        detail += " — " + "; ".join(problems)
    return detail


def _flatten_errors(errors) -> list[str]:
    """Error entries as strings, descending into the import API's
    per-work ``errors`` lists and field/message pairs."""
    flat = []
    for error in errors:
        if isinstance(error, dict):
            if isinstance(error.get("errors"), list):
                flat.extend(_flatten_errors(error["errors"]))
                continue
            if "message" in error:
                field = error.get("field")
                flat.append(
                    f"{field}: {error['message']}" if field else str(error["message"])
                )
                continue
        flat.append(str(error))
    return flat


def _retry_delay(response, attempt: int) -> float:
    """Seconds to wait before retrying: the server's Retry-After when
    given, else an exponential backoff (1, 2, 4, ... seconds)."""
    header = getattr(response, "headers", {}).get("Retry-After")
    try:
        return max(float(header), 1.0)
    except (TypeError, ValueError):
        return float(2**attempt)
