"""Gatekeeping for the inbound webhook.

Four independent checks, all of which must pass before an email is
believed: the Mailgun HMAC signature (proves the POST came from
Mailgun), a token replay guard (a captured POST cannot be replayed),
the sender allowlist (only Martin's addresses may publish), and
Mailgun's SPF/DKIM verdicts on the inbound message (a forged From on
someone else's infrastructure fails these). Nothing here sends mail;
rejected requests must stay silent to avoid backscatter.
"""

import email
import hashlib
import hmac
import json
import logging
import os
import re
import time
from email.utils import parseaddr
from pathlib import Path

import dkim
import requests

logger = logging.getLogger(__name__)

# Verdict headers Mailgun stamps on received messages (values such as
# "Pass", "Neutral", "Fail", "SoftFail").
SPF_HEADER = "X-Mailgun-Spf"
DKIM_HEADER = "X-Mailgun-Dkim-Check-Result"

SIGNATURE_TOLERANCE = 300  # seconds of clock skew tolerated


def verify_signature(
    signing_key: str,
    timestamp: str,
    token: str,
    signature: str,
    now: float | None = None,
    tolerance: int = SIGNATURE_TOLERANCE,
) -> bool:
    """True when the POST authenticates as Mailgun's.

    signature must equal HMAC-SHA256(signing_key, timestamp + token) in
    hex (compared timing-safely) and timestamp must be within
    ``tolerance`` seconds of ``now`` — a valid but stale signature is a
    replay, not a delivery.
    """
    try:
        posted_at = float(timestamp)
    except (TypeError, ValueError):
        return False
    if abs((now if now is not None else time.time()) - posted_at) > tolerance:
        return False
    expected = hmac.new(
        signing_key.encode(), f"{timestamp}{token}".encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature or "")


class SeenLedger:
    """A file-backed set of values with a time-to-live.

    Used twice: webhook tokens (replay protection) and Message-Ids
    (Mailgun retries must not publish a thought twice). Values expire
    so the file cannot grow without bound.
    """

    def __init__(self, path: Path, ttl_seconds: int = 7 * 86400):
        self.path = Path(path)
        self.ttl_seconds = ttl_seconds

    def seen_before(self, value: str, now: float | None = None) -> bool:
        """True when the value was recorded earlier; records it if not."""
        now = now if now is not None else time.time()
        entries = {
            seen: at
            for seen, at in _load(self.path).items()
            if now - at < self.ttl_seconds
        }
        already = value in entries
        if not already:
            entries[value] = now
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(entries), encoding="utf-8")
        return already


def sender_address(from_header: str) -> str:
    """The bare, lowercased address from an RFC 5322 From header."""
    return parseaddr(from_header or "")[1].lower()


def sender_allowed(from_header: str, allowed: frozenset) -> bool:
    """True when the From address is on the allowlist."""
    address = sender_address(from_header)
    return bool(address) and address in allowed


def auth_results(message_headers: str) -> dict:
    """Mailgun's SPF/DKIM verdicts from the message-headers JSON dump.

    Returns {"spf": value, "dkim": value} with "" for a missing header
    (header-name lookup is case-insensitive).
    """
    results = {"spf": "", "dkim": ""}
    try:
        headers = json.loads(message_headers or "[]")
    except json.JSONDecodeError:
        return results
    wanted = {SPF_HEADER.lower(): "spf", DKIM_HEADER.lower(): "dkim"}
    for entry in headers:
        try:
            name, value = entry[0], entry[1]
        except (TypeError, IndexError, KeyError):
            continue
        key = wanted.get(str(name).lower())
        if key and not results[key]:
            results[key] = str(value)
    return results


def is_authenticated(results: dict) -> bool:
    """True when both SPF and DKIM verdicts are Pass (any case)."""
    return (
        results.get("spf", "").lower() == "pass"
        and results.get("dkim", "").lower() == "pass"
    )


def stored_message_mime(
    config,
    message_id: str,
    get=None,
    attempts: int = 13,
    delay: float = 10.0,
    timeout: float = 15.0,
    sleep=None,
) -> bytes | None:
    """The raw MIME of a stored inbound message, or None.

    Mailgun stores every received message for a few days; this looks
    the message up in the Events API by Message-Id and retrieves the
    raw MIME from the storage URL. The events query must NOT filter by
    event type: a forward()-only route never emits a "stored" event —
    the storage block rides on its accepted/failed events instead (and
    failed events carry storage.url as a list, not a string). None
    means "not retrievable right now" — the caller decides whether
    that is a retry-later or a rejection. ``attempts``/``delay`` set
    the polling budget for the Events API's ingestion lag.
    """
    get = get or requests.get
    sleep = sleep or time.sleep
    clean_id = (message_id or "").strip().strip("<>")
    if not clean_id:
        return None
    events_url = (
        f"{config.mailgun_api_base}/v3/{config.mailgun_domain}/events"
    )
    auth = ("api", config.mailgun_api_key)
    saw_not_found = False
    reported = set()  # storage URLs already logged with a curl command
    for attempt in range(attempts):
        if attempt:
            sleep(delay)
        try:
            events = get(
                events_url,
                auth=auth,
                params={"message-id": clean_id},
                timeout=timeout,
            )
            items = (
                events.json().get("items", [])
                if events.status_code == 200
                else []
            )
        except Exception as exc:  # noqa: BLE001 — an API hiccup is just "not yet"
            logger.info(
                "event lookup for %r (attempt %d/%d) failed: %s",
                clean_id, attempt + 1, attempts, exc,
            )
            items = []
        candidates = storage_candidates(items)
        if candidates and not reported:
            logger.info(
                "events for %r carry %d storage URL(s) from event type(s) "
                "%s — a route whose store() ran must also show a 'stored' "
                "event here", clean_id, len(candidates),
                sorted({event for event, _ in candidates}),
            )
        for event, url in candidates:
            try:
                stored = get(
                    url,
                    auth=auth,
                    headers={"Accept": "message/rfc2822"},
                    timeout=timeout * 2,
                )
                if stored.status_code != 200:
                    if stored.status_code == 404:
                        saw_not_found = True
                    if url not in reported:
                        reported.add(url)
                        logger.info(
                            "storage fetch for %r (%s event) answered %s — "
                            "test it by hand with: %s",
                            clean_id, event, stored.status_code,
                            retrieval_curl(url),
                        )
                    else:
                        logger.info(
                            "storage fetch for %r (%s event) answered %s",
                            clean_id, event, stored.status_code,
                        )
                    continue
                mime = stored.json().get("body-mime") or ""
            except Exception as exc:  # noqa: BLE001 — a fetch hiccup is just "not yet"
                logger.info("storage fetch for %r failed: %s", clean_id, exc)
                continue
            if mime:
                return mime.encode() if isinstance(mime, str) else mime
    if saw_not_found:
        logger.warning(
            "every storage fetch for %r answered 404: Mailgun events "
            "carry storage URLs but no stored copy was retrievable. "
            "Either the matched route has no store() action, or its "
            "store() never ran (check which route actually matched, "
            "and that the events above include a 'stored' event — "
            "only store() emits one). Inspect the raw events with: "
            "curl -sS --user \"api:$MAILGUN_API_KEY\" '%s?message-id=%s'",
            clean_id, events_url, clean_id,
        )
    return None


# Raw MIME copies only need to outlive the worker's verification
# polling window; a day is generous. The file cap bounds disk use
# against a flood of signed-but-forged deliveries.
MIME_STASH_TTL_SECONDS = 86400
MIME_STASH_MAX_FILES = 256


class MimeStash:
    """Raw MIME copies POSTed to /inbound/mime, keyed by Message-Id.

    The Mailgun route's second forward action (a URL ending in "mime")
    delivers the full raw message; the webhook writes it here and the
    worker reads it back for DKIM verification. Message-Ids are hashed
    into filenames, so hostile ids cannot escape the directory.
    """

    def __init__(
        self,
        path: Path,
        ttl_seconds: int = MIME_STASH_TTL_SECONDS,
        max_files: int = MIME_STASH_MAX_FILES,
    ):
        self.path = Path(path)
        self.ttl_seconds = ttl_seconds
        self.max_files = max_files

    def _file(self, message_id: str) -> Path:
        clean = (message_id or "").strip().strip("<>")
        digest = hashlib.sha256(clean.encode()).hexdigest()
        return self.path / f"{digest}.eml"

    def save(self, message_id: str, raw: bytes, now: float | None = None) -> None:
        now = now if now is not None else time.time()
        self.path.mkdir(parents=True, exist_ok=True)
        for stale in self.path.glob("*.eml"):
            try:
                if now - stale.stat().st_mtime >= self.ttl_seconds:
                    stale.unlink()
            except OSError:
                continue
        target = self._file(message_id)
        if target.exists():
            # First write wins: a later, differing copy for the same
            # Message-Id would let a forger replace the genuine raw
            # message after it arrived. (Identical bytes are just a
            # Mailgun redelivery.)
            try:
                if target.read_bytes() != raw:
                    logger.warning(
                        "a differing raw MIME copy for %r arrived after "
                        "the first; keeping the first (possible "
                        "Message-Id reuse)", message_id,
                    )
            except OSError:
                pass
            return
        survivors = sorted(
            self.path.glob("*.eml"), key=lambda path: path.stat().st_mtime
        )
        for oldest in survivors[: max(0, len(survivors) - self.max_files + 1)]:
            oldest.unlink(missing_ok=True)
        target.write_bytes(raw)
        os.utime(target, (now, now))

    def load(self, message_id: str, now: float | None = None) -> bytes | None:
        now = now if now is not None else time.time()
        target = self._file(message_id)
        try:
            if now - target.stat().st_mtime >= self.ttl_seconds:
                return None
            return target.read_bytes()
        except OSError:
            return None


def verification_mime(
    config,
    message_id: str,
    stash=None,
    attempts: int = 25,
    delay: float = 5.0,
    sleep=None,
    get=None,
) -> bytes | None:
    """Raw MIME for deferred DKIM verification, or None.

    Polls the local stash (filled by the route's forward to
    /inbound/mime) first — that copy normally arrives within seconds
    of the parsed webhook POST. Only if it never shows up is Mailgun's
    storage API tried once, for deployments whose plan still allows
    message retrieval.
    """
    stash = stash if stash is not None else MimeStash(config.mime_dir)
    sleep = sleep or time.sleep
    for attempt in range(attempts):
        if attempt:
            sleep(delay)
        raw = stash.load(message_id)
        if raw is not None:
            return raw
    logger.warning(
        "no raw MIME copy of %r ever arrived at /inbound/mime — check "
        "that the Mailgun route has a second forward action whose URL "
        "ends in /inbound/mime. Trying Mailgun's storage API as a "
        "fallback (it answers 405 on plans without message retrieval)",
        message_id,
    )
    return stored_message_mime(
        config, message_id, get=get, attempts=1, sleep=sleep
    )


def retrieval_curl(url: str) -> str:
    """A copy-pasteable curl equivalent of a storage fetch.

    The API key is referenced as $MAILGUN_API_KEY so the command is
    safe to log; export the real key before running it.
    """
    return (
        "curl -sS --user \"api:$MAILGUN_API_KEY\" "
        f"-H 'Accept: message/rfc2822' '{url}'"
    )


def storage_candidates(items: list) -> list:
    """(event type, storage URL) pairs found across Mailgun events."""
    pairs = []
    for item in items:
        event = str(item.get("event") or "?")
        url = (item.get("storage") or {}).get("url") or ""
        if isinstance(url, list):
            pairs.extend((event, part) for part in url if part)
        elif url:
            pairs.append((event, url))
    return pairs


def content_bound(
    raw_mime: bytes, sender: str, text: str, images: list
) -> bool:
    """True when the job's content is present in the verified message.

    DKIM proves the raw message is authentic; this proves the content
    about to be published came from *that* message rather than from a
    second, forged delivery reusing its Message-Id: the raw From must
    be the job's sender, every job image's bytes must be an attachment
    of the raw message, and the job text must appear in its text/plain
    body (whitespace-insensitively; HTML-only mail has no text/plain
    part and skips the text check).
    """
    if not raw_mime:
        return False
    message = email.message_from_bytes(raw_mime)
    if sender_address(message.get("From", "")) != (sender or "").strip().lower():
        return False
    plain_parts, attachment_blobs = [], []
    for part in message.walk():
        if part.is_multipart():
            continue
        payload = part.get_payload(decode=True) or b""
        if part.get_content_type() == "text/plain" and "attachment" not in str(
            part.get("Content-Disposition") or ""
        ):
            charset = part.get_content_charset() or "utf-8"
            try:
                plain_parts.append(payload.decode(charset, "replace"))
            except LookupError:
                plain_parts.append(payload.decode("utf-8", "replace"))
        else:
            attachment_blobs.append(payload)
    for blob in images:
        if blob not in attachment_blobs:
            return False
    wanted = _collapse(text)
    if wanted and plain_parts:
        return wanted in _collapse("\n".join(plain_parts))
    return True


def _collapse(text: str) -> str:
    """Whitespace-insensitive comparison form (flowed unwrapping,
    CRLF normalisation and trailing-line stripping all preserve it)."""
    return " ".join((text or "").split())


def dkim_authenticated(
    raw_mime: bytes, from_domain: str, dnsfunc=None
) -> bool:
    """True when the raw message carries a valid, aligned DKIM signature.

    A signature only counts if its d= domain aligns with the From
    address's domain (equal, or one a subdomain of the other) — a valid
    signature from an unrelated domain proves nothing about the From
    header. ``dnsfunc`` is injectable for tests; None uses live DNS.
    """
    if not raw_mime or not from_domain:
        return False
    wanted = from_domain.strip().lower().rstrip(".")
    signatures = (
        email.message_from_bytes(raw_mime).get_all("DKIM-Signature") or []
    )
    kwargs = {"dnsfunc": dnsfunc} if dnsfunc is not None else {}
    for index, header in enumerate(signatures):
        match = re.search(r"\bd\s*=\s*([^;\s]+)", str(header))
        signer = match.group(1).strip().lower().rstrip(".") if match else ""
        if not signer or not _domains_aligned(signer, wanted):
            continue
        try:
            if dkim.DKIM(raw_mime).verify(idx=index, **kwargs):
                return True
        except Exception as exc:  # noqa: BLE001 — a broken signature is just a non-pass
            logger.info(
                "DKIM signature %d (d=%r) did not verify: %s",
                index, signer, exc,
            )
            continue
    return False


def _domains_aligned(signer: str, from_domain: str) -> bool:
    """Relaxed alignment: equal, or one a subdomain of the other."""
    return (
        signer == from_domain
        or from_domain.endswith("." + signer)
        or signer.endswith("." + from_domain)
    )


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
