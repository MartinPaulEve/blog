"""A minimal Mastodon client for posting thought threads."""

import time

import requests

BASE_URL = "https://hcommons.social"
PROCESSING_POLLS = 30
# A media upload is the one large transfer here, and a lossy link (a
# tethered phone, say) can corrupt a TLS record mid-way — surfacing as an
# SSLError "bad record mac", a ConnectionError. Those are worth a few
# retries; a rejected upload (an HTTP error) is not.
UPLOAD_ATTEMPTS = 3
UPLOAD_RETRY_DELAY = 2.0


class MastodonError(RuntimeError):
    """An API request that the Mastodon server rejected."""


def _checked(response) -> dict:
    if 200 <= response.status_code < 300:
        return response.json()
    raise MastodonError(f"HTTP {response.status_code}: {response.text[:300]}")


class MastodonClient:
    """Posts statuses with a bearer token.

    Media are uploaded first (polling while the server processes them)
    and attached to the first status; later segments reply to the one
    before, forming a thread. Link previews are generated server-side
    by Mastodon itself, so URLs just need to appear in the text.
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        session=None,
        sleep=time.sleep,
    ):
        self.base_url = base_url.rstrip("/")
        self._session = session if session is not None else requests.Session()
        self._headers = {"Authorization": f"Bearer {token}"}
        self._sleep = sleep

    def verify(self) -> str:
        """Check the token; return the account's acct handle."""
        data = _checked(
            self._session.get(
                f"{self.base_url}/api/v1/accounts/verify_credentials",
                headers=self._headers,
            )
        )
        return data["acct"]

    def upload_media(self, data: bytes, mime: str, alt: str = "") -> str:
        """Upload one attachment; return its media id once processed.

        Connection-level failures (SSL errors, resets, timeouts) are
        retried a bounded number of times; the server's answer, once it
        arrives, is taken as final.
        """
        for attempt in range(1, UPLOAD_ATTEMPTS + 1):
            try:
                response = self._session.post(
                    f"{self.base_url}/api/v2/media",
                    headers=self._headers,
                    files={"file": ("attachment", data, mime)},
                    data={"description": alt},
                )
                break
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout):
                if attempt == UPLOAD_ATTEMPTS:
                    raise
                self._sleep(UPLOAD_RETRY_DELAY * attempt)
        if response.status_code == 202:
            media_id = response.json()["id"]
            for _ in range(PROCESSING_POLLS):
                poll = self._session.get(
                    f"{self.base_url}/api/v1/media/{media_id}",
                    headers=self._headers,
                )
                if poll.status_code == 200:
                    return media_id
                self._sleep(1)
            raise MastodonError("media processing timed out")
        return _checked(response)["id"]

    def post_thread(
        self,
        segments: list[str],
        media_ids: list[str] | None = None,
    ) -> list[str]:
        """Publish segments as a thread; return the status URLs."""
        urls = []
        previous_id = None
        for index, segment in enumerate(segments):
            payload = {"status": segment, "visibility": "public"}
            if index == 0 and media_ids:
                payload["media_ids"] = list(media_ids)
            if previous_id:
                payload["in_reply_to_id"] = previous_id
            data = _checked(
                self._session.post(
                    f"{self.base_url}/api/v1/statuses",
                    headers=self._headers,
                    json=payload,
                )
            )
            previous_id = data["id"]
            urls.append(data["url"])
        return urls
