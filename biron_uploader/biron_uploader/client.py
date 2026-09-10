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
    """The new object's identity from a SWORD/CRUD deposit response.

    Returns ``{"eprintid", "url"}`` where url is the canonical
    /id/<dataset>/NNNNN/ form. The id comes from the Location header or
    the entry id in the body — BIROn variously answers with a Location
    carrying a /contents suffix and with un-namespaced <entry> bodies,
    so both are normalized.
    """
    candidates = []
    if headers.get("Location"):
        candidates.append(headers["Location"])
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        root = None
    if root is not None:
        for tag in (f"{ATOM_NS}id", "id"):
            entry_id = root.find(tag)
            if entry_id is not None and entry_id.text:
                candidates.append(entry_id.text)

    for candidate in candidates:
        candidate = candidate.strip().rstrip("/")
        candidate = candidate.removesuffix("/contents")
        m = re.search(r"/(\d+)$", candidate)
        if m:
            return {"eprintid": int(m.group(1)), "url": candidate + "/"}
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
        username: str | None = None,
        password: str | None = None,
        base_url: str = BASE_URL,
        session=None,
        max_retries: int = 3,
        sleep=time.sleep,
        cookie: str | None = None,
    ):
        if not cookie and not (username and password):
            raise ValueError(
                "BironClient needs a session cookie or username+password"
            )
        self.base_url = base_url.rstrip("/")
        self._auth = (username, password)
        self._cookie = cookie
        self._session = session if session is not None else requests.Session()
        self._max_retries = max_retries
        self._sleep = sleep

    def _credentials(self, kwargs: dict) -> dict:
        """Fold our credentials into request kwargs (cookie beats Basic)."""
        if self._cookie:
            kwargs.setdefault("headers", {})["Cookie"] = self._cookie
        else:
            kwargs["auth"] = self._auth
        return kwargs

    def contents_status(self) -> int:
        """The HTTP status of GET /id/contents with our credentials.

        A cheap authentication probe for the CRUD endpoint, which sits
        behind EPrints' standard auth chain (session cookie accepted)
        even when /sword-app only parses Basic credentials.
        """
        response = self._session.get(
            f"{self.base_url}/id/contents", **self._credentials({})
        )
        return response.status_code

    def _send(self, method: str, url: str, **kwargs):
        """Issue a request, retrying rate limits and transient errors."""
        kwargs = self._credentials(kwargs)
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

    def eprint_status(self, eprintid: int) -> str | None:
        """The eprint_status of a record, or None when unreadable."""
        response = self._session.get(
            f"{self.base_url}/id/eprint/{eprintid}",
            **self._credentials(
                {"headers": {"Accept": "application/vnd.eprints.data+xml"}}
            ),
        )
        if response.status_code != 200:
            return None
        try:
            status = ET.fromstring(response.content).find(
                ".//{http://eprints.org/ep2/data/2.0}eprint_status"
            )
        except ET.ParseError:
            return None
        return None if status is None else status.text

    def deposit(
        self,
        collection_url: str,
        xml: bytes,
        documents=None,
        make_live: bool = False,
    ) -> dict:
        """Create an eprint from metadata XML, then attach its documents.

        /sword-app collections read the X-Packaging header; the /id/
        CRUD endpoint keys its import plugin off the Content-Type
        instead. With ``make_live``, a record the server parked in the
        workarea is PUT back (same XML, carrying eprint_status archive)
        while it is still documentless, so nothing can be wiped.

        ``documents`` is ``[{"xml", "filename", "mime", "data"}]``:
        each document is created from its metadata XML (carrying the
        required security field) and its bytes arrive as a raw PUT —
        never as inline base64, which BIROn's importer corrupts.
        Returns the parsed receipt ``{"eprintid", "url"}``.
        """
        headers = {"X-Packaging": PACKAGING}
        if "/id/" in collection_url:
            headers["Content-Type"] = "application/vnd.eprints.data+xml"
            # SWORD2 semantics: the deposit is complete, not a work in
            # progress to be held in the depositor's workarea.
            headers["In-Progress"] = "false"
        else:
            headers["Content-Type"] = "application/xml; charset=utf-8"
        response = self._send("post", collection_url, data=xml, headers=headers)
        receipt = parse_deposit_receipt(response.headers, response.content)
        eprint_url = f"{self.base_url}/id/eprint/{receipt['eprintid']}"

        if make_live and self.eprint_status(receipt["eprintid"]) != "archive":
            self._send(
                "put",
                eprint_url,
                data=xml,
                headers={"Content-Type": "application/vnd.eprints.data+xml"},
            )

        try:
            for document in documents or []:
                created = self._send(
                    "post",
                    f"{eprint_url}/contents",
                    data=document["xml"],
                    headers={
                        "Content-Type": "application/vnd.eprints.data+xml",
                        "In-Progress": "false",
                    },
                )
                doc = parse_deposit_receipt(created.headers, created.content)
                self._send(
                    "put",
                    f"{self.base_url}/id/document/{doc['eprintid']}/contents",
                    data=document["data"],
                    headers={
                        "Content-Type": document["mime"],
                        "Content-Disposition": (
                            f'attachment; filename="{document["filename"]}"'
                        ),
                    },
                )
        except BironError as exc:
            raise BironError(
                f"eprint {receipt['eprintid']} was created but attaching "
                f"{document['filename']} failed — delete the record "
                f"({receipt['url']}) before retrying. Cause: {exc}"
            ) from exc
        return receipt
