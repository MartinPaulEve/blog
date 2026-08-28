"""A minimal KC Works (InvenioRDM) API client for draft records."""

from pathlib import Path

import requests


class KCWorksError(RuntimeError):
    """An API request that the KC Works server rejected."""


class KCWorksClient:
    """Talks to the KC Works records API with a bearer token."""

    def __init__(self, base_url: str, token: str, session=None):
        self.base_url = base_url.rstrip("/")
        self._session = session if session is not None else requests.Session()
        self._session.headers["Authorization"] = f"Bearer {token}"

    def create_draft(self, record: dict) -> dict:
        """POST the record JSON to /records; return the created draft JSON."""
        return self._checked(
            self._session.post(f"{self.base_url}/records", json=record)
        )

    def update_draft(self, draft_id: str, record: dict) -> dict:
        """PUT the record JSON to an existing draft; return the updated JSON.

        Needed to set files.default_preview: the server drops it at
        creation time because the file does not exist yet, so the draft
        must be updated again once the uploads are committed.
        """
        return self._checked(
            self._session.put(
                f"{self.base_url}/records/{draft_id}/draft", json=record
            )
        )

    def publish_draft(self, draft_id: str) -> dict:
        """POST the publish action for a draft; return the published record."""
        return self._checked(
            self._session.post(
                f"{self.base_url}/records/{draft_id}/draft/actions/publish"
            )
        )

    def upload_files(self, draft_id: str, paths: list[Path]) -> list[str]:
        """Attach files to a draft: initiate, upload content, commit each.

        Returns the list of committed file keys.
        """
        paths = [Path(path) for path in paths]
        files_url = f"{self.base_url}/records/{draft_id}/draft/files"
        self._checked(
            self._session.post(
                files_url, json=[{"key": path.name} for path in paths]
            )
        )
        for path in paths:
            with path.open("rb") as handle:
                self._checked(
                    self._session.put(
                        f"{files_url}/{path.name}/content",
                        data=handle,
                        headers={"Content-Type": "application/octet-stream"},
                    )
                )
            self._checked(self._session.post(f"{files_url}/{path.name}/commit"))
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
