"""A minimal SWORD 1.3 client for EPrints (BIROn), using HTTP Basic auth."""

import re
import time
import xml.etree.ElementTree as ET

import requests

BASE_URL = "https://eprints.bbk.ac.uk"
SERVICE_DOCUMENT_PATH = "/sword-app/servicedocument"
PACKAGING = "http://eprints.org/ep2/data/2.0"
RETRY_STATUSES = {429, 500, 502, 503, 504}


class BironError(RuntimeError):
    """A SWORD request that the BIROn server rejected."""


APP_NS = "{http://www.w3.org/2007/app}"
ATOM_NS = "{http://www.w3.org/2005/Atom}"
SWORD_NS = "{http://purl.org/net/sword/}"
EPRINT_URL_RE = re.compile(r"^(?:https?://\S+?)/(\d+)/?$")


def parse_service_document(xml: bytes) -> list[dict]:
    """The deposit collections in a SWORD service document.

    Returns ``[{"href", "title", "packaging"}]`` where packaging is the
    list of accepted packaging identifiers for the collection.
    """
    root = ET.fromstring(xml)
    collections = []
    for coll in root.iter(f"{APP_NS}collection"):
        title = coll.find(f"{ATOM_NS}title")
        collections.append(
            {
                "href": coll.get("href"),
                "title": None if title is None else title.text,
                "packaging": [
                    p.text for p in coll.findall(f"{SWORD_NS}acceptPackaging")
                ],
            }
        )
    return collections


def parse_deposit_receipt(headers: dict, body: bytes) -> dict:
    """The new eprint's identity from a SWORD deposit response.

    Returns ``{"eprintid", "url"}`` where url is the canonical
    https://eprints.bbk.ac.uk/id/eprint/NNNNN/ form. The id is taken
    from the Location header when present, else from the Atom entry id.
    """
    candidates = []
    if headers.get("Location"):
        candidates.append(headers["Location"])
    else:
        try:
            atom_id = ET.fromstring(body).find(f"{ATOM_NS}id")
        except ET.ParseError:
            atom_id = None
        if atom_id is not None and atom_id.text:
            candidates.append(atom_id.text)

    for candidate in candidates:
        m = EPRINT_URL_RE.match(candidate.strip())
        if m:
            return {
                "eprintid": int(m.group(1)),
                "url": candidate.strip().rstrip("/") + "/",
            }
    raise BironError(
        "deposit response carried no eprint id "
        f"(Location: {headers.get('Location')!r}; body starts "
        f"{body[:120]!r})"
    )


def _retry_delay(response, attempt: int) -> float:
    retry_after = response.headers.get("Retry-After")
    if retry_after and str(retry_after).isdigit():
        return int(retry_after)
    return 2**attempt


class BironClient:
    """Talks SWORD 1.3 to an EPrints repository with Basic auth.

    Rate limits (429) and transient server errors (5xx) are retried
    with a backoff wait before an error is finally raised.
    """

    def __init__(
        self,
        username: str,
        password: str,
        base_url: str = BASE_URL,
        session=None,
        max_retries: int = 3,
        sleep=time.sleep,
    ):
        self.base_url = base_url.rstrip("/")
        self._auth = (username, password)
        self._session = session if session is not None else requests.Session()
        self._max_retries = max_retries
        self._sleep = sleep

    def _send(self, method: str, url: str, **kwargs):
        """Issue a request, retrying rate limits and transient errors."""
        kwargs["auth"] = self._auth
        for attempt in range(self._max_retries + 1):
            response = getattr(self._session, method)(url, **kwargs)
            if (
                response.status_code not in RETRY_STATUSES
                or attempt == self._max_retries
            ):
                return self._checked(response)
            self._sleep(_retry_delay(response, attempt))
        raise AssertionError("unreachable")

    @staticmethod
    def _checked(response):
        if 200 <= response.status_code < 300:
            return response
        raise BironError(
            f"HTTP {response.status_code}: {response.text[:300]}"
        )

    def service_document(self) -> list[dict]:
        """GET the service document; return its deposit collections."""
        response = self._send(
            "get", f"{self.base_url}{SERVICE_DOCUMENT_PATH}"
        )
        return parse_service_document(response.content)

    def deposit(self, collection_url: str, xml: bytes) -> dict:
        """POST an EPrints XML package to a collection.

        Returns the parsed deposit receipt ``{"eprintid", "url"}``.
        """
        response = self._send(
            "post",
            collection_url,
            data=xml,
            headers={
                "Content-Type": "application/xml; charset=utf-8",
                "X-Packaging": PACKAGING,
            },
        )
        return parse_deposit_receipt(response.headers, response.content)
