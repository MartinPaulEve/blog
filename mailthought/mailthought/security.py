"""Gatekeeping for the inbound webhook.

Four independent checks, all of which must pass before an email is
believed: the Mailgun HMAC signature (proves the POST came from
Mailgun), a token replay guard (a captured POST cannot be replayed),
the sender allowlist (only Martin's addresses may publish), and
Mailgun's SPF/DKIM verdicts on the inbound message (a forged From on
someone else's infrastructure fails these). Nothing here sends mail;
rejected requests must stay silent to avoid backscatter.
"""

import hashlib
import hmac
import json
import time
from email.utils import parseaddr
from pathlib import Path

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


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
