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
    sleep=None,
) -> bytes | None:
    """The raw MIME of a stored inbound message, or None.

    Mailgun stores every received message for a few days; this looks
    the message up in the Events API by Message-Id and retrieves the
    raw MIME from the storage URL the stored event carries. None means
    "not retrievable right now" — the caller decides whether that is
    a retry-later or a rejection. The Events API can lag reception by
    minutes, so the lookup polls for around two of them (the defaults:
    twelve ``delay``-second waits between thirteen attempts) — far
    better than bouncing to Mailgun's ~10-minute redelivery cycle.
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
    for attempt in range(attempts):
        if attempt:
            sleep(delay)
        try:
            events = get(
                events_url,
                auth=auth,
                params={"event": "stored", "message-id": clean_id},
                timeout=15,
            )
            items = (
                events.json().get("items", [])
                if events.status_code == 200
                else []
            )
        except Exception as exc:  # noqa: BLE001 — an API hiccup is just "not yet"
            logger.info(
                "stored-event lookup for %r (attempt %d/%d) failed: %s",
                clean_id, attempt + 1, attempts, exc,
            )
            items = []
        for item in items:
            url = (item.get("storage") or {}).get("url") or ""
            if not url:
                continue
            try:
                stored = get(
                    url,
                    auth=auth,
                    headers={"Accept": "message/rfc2822"},
                    timeout=30,
                )
                if stored.status_code != 200:
                    logger.info(
                        "storage fetch for %r answered %s",
                        clean_id, stored.status_code,
                    )
                    continue
                mime = stored.json().get("body-mime") or ""
            except Exception as exc:  # noqa: BLE001 — a fetch hiccup is just "not yet"
                logger.info("storage fetch for %r failed: %s", clean_id, exc)
                continue
            if mime:
                return mime.encode() if isinstance(mime, str) else mime
    return None


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
