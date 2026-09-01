"""A minimal KC Works (InvenioRDM) API client for draft records."""

import time
from pathlib import Path

import requests

RETRY_STATUSES = {429, 500, 502, 503, 504}


class KCWorksError(RuntimeError):
    """An API request that the KC Works server rejected."""


class KCWorksClient:
    """Talks to the KC Works records API with a bearer token.

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

    def _send(self, method: str, url: str, **kwargs) -> dict:
        """Issue a request, retrying rate limits and transient errors."""
        for attempt in range(self._max_retries + 1):
            response = getattr(self._session, method)(url, **kwargs)
            if (
                response.status_code not in RETRY_STATUSES
                or attempt == self._max_retries
            ):
                return self._checked(response)
            self._sleep(_retry_delay(response, attempt))
        raise AssertionError("unreachable")

    def create_draft(self, record: dict) -> dict:
        """POST the record JSON to /records; return the created draft JSON."""
        return self._send("post", f"{self.base_url}/records", json=record)

    def update_draft(self, draft_id: str, record: dict) -> dict:
        """PUT the record JSON to an existing draft; return the updated JSON.

        Needed to set files.default_preview: the server drops it at
        creation time because the file does not exist yet, so the draft
        must be updated again once the uploads are committed.
        """
        return self._send(
            "put", f"{self.base_url}/records/{draft_id}/draft", json=record
        )

    def publish_draft(self, draft_id: str) -> dict:
        """POST the publish action for a draft; return the published record."""
        return self._send(
            "post",
            f"{self.base_url}/records/{draft_id}/draft/actions/publish",
        )

    def upload_files(self, draft_id: str, paths: list[Path]) -> list[str]:
        """Attach files to a draft: initiate, upload content, commit each.

        Returns the list of committed file keys. Contents are sent as
        bytes so a rate-limited upload can be safely retried.
        """
        paths = [Path(path) for path in paths]
        files_url = f"{self.base_url}/records/{draft_id}/draft/files"
        self._send(
            "post", files_url, json=[{"key": path.name} for path in paths]
        )
        for path in paths:
            self._send(
                "put",
                f"{files_url}/{path.name}/content",
                data=path.read_bytes(),
                headers={"Content-Type": "application/octet-stream"},
            )
            self._send("post", f"{files_url}/{path.name}/commit")
        return [path.name for path in paths]

    @staticmethod
    def _checked(response) -> dict:
        if response.status_code not in (200, 201, 202):
            try:
                payload = response.json()
                detail = str(payload.get("message") or payload)
                if payload.get("errors"):
                    detail += f" — {payload['errors']}"
            except ValueError:
                detail = response.text
            raise KCWorksError(
                f"KC Works returned HTTP {response.status_code}: {detail}"
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


def _retry_delay(response, attempt: int) -> float:
    """Seconds to wait before retrying: the server's Retry-After when
    given, else an exponential backoff (1, 2, 4, ... seconds)."""
    header = getattr(response, "headers", {}).get("Retry-After")
    try:
        return max(float(header), 1.0)
    except (TypeError, ValueError):
        return float(2**attempt)
