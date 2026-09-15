"""security: webhook signature, replay ledger, allowlist, SPF/DKIM verdicts."""

import json

import dkim
from conftest import sign

from mailthought.security import (
    SeenLedger,
    auth_results,
    dkim_authenticated,
    is_authenticated,
    sender_address,
    sender_allowed,
    stored_message_mime,
    verify_signature,
)

KEY = "signing-secret"

# A throwaway 1024-bit RSA pair for DKIM round-trips: tests sign a
# message with the private half and serve the public half through a
# fake dnsfunc, so verification is real dkimpy work with no network.
DKIM_PRIVATE_KEY = b"""-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQDjBv3CSS4tzk1VKcGHeKl3Ncdttip8TA1WcO7aBSR6g2+EO2Ox
UEeTXpUHRGQ4fCjbnGjfO9g5sn9UhM0S6uO5/ouHnPqN/tRUs6QRnWYr5AVyFJsp
QSsecyavQXXDNrDXXDPNNPxZoW/A423xMXa8dMZhI9N7nPbi81lhLA+dyQIDAQAB
AoGAAUyN8SmoCP0QNjeJ8vN+zL7TCE6tiY6J2P/GbhrvbYAJCFGqrV4POsmkwqji
hew386G+e+CEyTe7QMmNvtj3Opt29mQ2v81XpAtuFpaARHHTLcbyT2X3xcx5FN6y
Cw+Hbo89RzQ83OuwbGmXGV2WnBrPLCfZsdLek876xdn0nB0CQQDykV5v1vqNoEUK
qGQ0tdwAFyrnFTfaC02swZYcEj8fcgjHQ/xSFIatQkkILV4B2easm46Q91J90Cye
YONuGniLAkEA75lSBBU6og2RUYLVSLPDMrHK2NAeRN/N4GsCFm3sJe2CWPkSEfa8
DITHuBZHn5Y3zMG3QFwKswQdt4951Np5ewJANm05xFx3Uanhc/e+rDkWCQspvDn9
kzYwEpBJTzkk4rhikduGVSB3645Q9r2/NykeYiJxRcPIxaQdLthMj5ru6wJBAJPI
ptzb10FzSunS4Akqz8BqB2r522GyBYNhnXUGMf0m5RpJ7opj/JNgJuv12hGmDx7d
cVFiNDs807OP7J6MbxcCQHj87d4ujMZsY2Kw51mCR6g2FzmSpVbBCbsIsh3MFlr/
G1JSot6ZMloQqZeojKmegWaZ1gBtkiUYP5msP48jBOg=
-----END RSA PRIVATE KEY-----
"""
DKIM_PUBLIC_KEY = (
    "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDjBv3CSS4tzk1VKcGHeKl3Ncdt"
    "tip8TA1WcO7aBSR6g2+EO2OxUEeTXpUHRGQ4fCjbnGjfO9g5sn9UhM0S6uO5/ouH"
    "nPqN/tRUs6QRnWYr5AVyFJspQSsecyavQXXDNrDXXDPNNPxZoW/A423xMXa8dMZh"
    "I9N7nPbi81lhLA+dyQIDAQAB"
)

DKIM_MESSAGE = (
    b"From: Martin Eve <martin@eve.gd>\r\n"
    b"To: thought@mg.eve.gd\r\n"
    b"Subject: hello\r\n"
    b"\r\n"
    b"a thought\r\n"
)


def dkim_sign(message: bytes, domain: bytes = b"eve.gd") -> bytes:
    header = dkim.sign(message, b"test", domain, DKIM_PRIVATE_KEY)
    return header + message


def dkim_dns(name, timeout=5):
    return ("v=DKIM1; k=rsa; p=" + DKIM_PUBLIC_KEY).encode()


class TestVerifySignature:
    def test_accepts_a_genuine_signature(self):
        assert verify_signature(
            KEY, "1000000000", "tok", sign(KEY, "1000000000", "tok"),
            now=1000000010,
        )

    def test_rejects_a_forged_signature(self):
        assert not verify_signature(
            KEY, "1000000000", "tok", "0" * 64, now=1000000010
        )

    def test_rejects_a_signature_made_with_another_key(self):
        assert not verify_signature(
            KEY, "1000000000", "tok", sign("other-key", "1000000000", "tok"),
            now=1000000010,
        )

    def test_rejects_a_stale_timestamp_even_when_validly_signed(self):
        assert not verify_signature(
            KEY, "1000000000", "tok", sign(KEY, "1000000000", "tok"),
            now=1000000000 + 3600,
        )

    def test_rejects_a_far_future_timestamp(self):
        assert not verify_signature(
            KEY, "1000003600", "tok", sign(KEY, "1000003600", "tok"),
            now=1000000000,
        )

    def test_rejects_garbage_timestamps_without_crashing(self):
        assert not verify_signature(KEY, "not-a-number", "tok", "sig")

    def test_rejects_empty_fields(self):
        assert not verify_signature(KEY, "", "", "")


class TestSeenLedger:
    def test_first_sighting_is_new_then_remembered(self, tmp_path):
        ledger = SeenLedger(tmp_path / "seen.json")
        assert ledger.seen_before("tok-1", now=1000.0) is False
        assert ledger.seen_before("tok-1", now=1001.0) is True

    def test_distinct_values_do_not_collide(self, tmp_path):
        ledger = SeenLedger(tmp_path / "seen.json")
        ledger.seen_before("tok-1", now=1000.0)
        assert ledger.seen_before("tok-2", now=1000.0) is False

    def test_memory_survives_a_restart(self, tmp_path):
        SeenLedger(tmp_path / "seen.json").seen_before("tok-1", now=1000.0)
        again = SeenLedger(tmp_path / "seen.json")
        assert again.seen_before("tok-1", now=1001.0) is True

    def test_entries_expire_after_the_ttl(self, tmp_path):
        ledger = SeenLedger(tmp_path / "seen.json", ttl_seconds=100)
        ledger.seen_before("tok-1", now=1000.0)
        assert ledger.seen_before("tok-1", now=1200.0) is False

    def test_creates_missing_parent_directories(self, tmp_path):
        ledger = SeenLedger(tmp_path / "state" / "deep" / "seen.json")
        assert ledger.seen_before("tok-1", now=1000.0) is False


class TestSenderChecks:
    def test_address_extracted_from_display_name_form(self):
        assert sender_address("Martin Eve <Martin@Eve.gd>") == "martin@eve.gd"

    def test_bare_address_passes_through_lowercased(self):
        assert sender_address("MARTIN@EVE.GD") == "martin@eve.gd"

    def test_allowed_sender_accepted_regardless_of_case(self):
        allowed = frozenset({"martin@eve.gd"})
        assert sender_allowed("Martin Eve <MARTIN@eve.gd>", allowed)

    def test_unknown_sender_rejected(self):
        allowed = frozenset({"martin@eve.gd"})
        assert not sender_allowed("Mallory <mallory@evil.example>", allowed)

    def test_display_name_cannot_impersonate_an_allowed_address(self):
        allowed = frozenset({"martin@eve.gd"})
        assert not sender_allowed(
            "martin@eve.gd <mallory@evil.example>", allowed
        )


class TestAuthResults:
    def test_verdicts_read_from_message_headers(self):
        headers = json.dumps(
            [
                ["Subject", "hi"],
                ["X-Mailgun-Spf", "Pass"],
                ["X-Mailgun-Dkim-Check-Result", "Pass"],
            ]
        )
        assert auth_results(headers) == {"spf": "Pass", "dkim": "Pass"}

    def test_header_name_lookup_is_case_insensitive(self):
        headers = json.dumps(
            [["x-mailgun-spf", "Pass"], ["X-MAILGUN-DKIM-CHECK-RESULT", "Fail"]]
        )
        assert auth_results(headers) == {"spf": "Pass", "dkim": "Fail"}

    def test_missing_headers_yield_empty_verdicts(self):
        assert auth_results(json.dumps([["Subject", "hi"]])) == {
            "spf": "",
            "dkim": "",
        }

    def test_unparseable_header_dump_yields_empty_verdicts(self):
        assert auth_results("not json") == {"spf": "", "dkim": ""}

    def test_both_passing_authenticates(self):
        assert is_authenticated({"spf": "Pass", "dkim": "Pass"})
        assert is_authenticated({"spf": "pass", "dkim": "PASS"})

    def test_any_other_verdict_fails(self):
        assert not is_authenticated({"spf": "Neutral", "dkim": "Pass"})
        assert not is_authenticated({"spf": "Pass", "dkim": "Fail"})
        assert not is_authenticated({"spf": "SoftFail", "dkim": "Pass"})
        assert not is_authenticated({"spf": "", "dkim": ""})


class TestDkimAuthenticated:
    """Direct DKIM verification, used when Mailgun's verdicts are absent."""

    def test_valid_aligned_signature_authenticates(self):
        signed = dkim_sign(DKIM_MESSAGE)
        assert dkim_authenticated(signed, "eve.gd", dnsfunc=dkim_dns) is True

    def test_subdomain_of_the_signing_domain_is_aligned(self):
        signed = dkim_sign(DKIM_MESSAGE)
        assert (
            dkim_authenticated(signed, "mail.eve.gd", dnsfunc=dkim_dns)
            is True
        )

    def test_valid_signature_from_an_unrelated_domain_fails(self):
        signed = dkim_sign(DKIM_MESSAGE, domain=b"evil.example")
        assert dkim_authenticated(signed, "eve.gd", dnsfunc=dkim_dns) is False

    def test_unsigned_message_fails(self):
        assert (
            dkim_authenticated(DKIM_MESSAGE, "eve.gd", dnsfunc=dkim_dns)
            is False
        )

    def test_tampered_body_fails(self):
        signed = dkim_sign(DKIM_MESSAGE)
        tampered = signed.replace(b"a thought", b"a forgery")
        assert (
            dkim_authenticated(tampered, "eve.gd", dnsfunc=dkim_dns) is False
        )

    def test_empty_inputs_fail_without_crashing(self):
        assert dkim_authenticated(b"", "eve.gd", dnsfunc=dkim_dns) is False
        signed = dkim_sign(DKIM_MESSAGE)
        assert dkim_authenticated(signed, "", dnsfunc=dkim_dns) is False


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


class TestStoredMessageMime:
    """Looking a stored message up by Message-Id and fetching its MIME."""

    STORAGE_URL = (
        "https://storage-europe-west1.api.mailgun.net/v3/domains/"
        "mg.eve.gd/messages/KEY123"
    )

    def fake_get(self, events_items):
        def get(url, **kwargs):
            if "/events" in url:
                params = kwargs.get("params") or {}
                if params.get("message-id") != "m1@eve.gd":
                    return FakeResponse(payload={"items": []})
                return FakeResponse(payload={"items": events_items})
            if url == self.STORAGE_URL:
                return FakeResponse(payload={"body-mime": "RAW MIME BYTES"})
            return FakeResponse(status_code=404)

        return get

    def test_fetches_the_raw_mime_for_a_stored_message(self, config):
        get = self.fake_get([{"storage": {"url": self.STORAGE_URL}}])
        assert (
            stored_message_mime(
                config, "<m1@eve.gd>", get=get, sleep=lambda s: None
            )
            == b"RAW MIME BYTES"
        )

    def test_returns_none_while_the_stored_event_is_not_yet_visible(
        self, config
    ):
        get = self.fake_get([])
        assert (
            stored_message_mime(
                config, "<m1@eve.gd>", get=get, sleep=lambda s: None
            )
            is None
        )

    def test_returns_none_when_the_api_errors(self, config):
        def get(url, **kwargs):
            raise OSError("connection refused")

        assert (
            stored_message_mime(
                config, "<m1@eve.gd>", get=get, sleep=lambda s: None
            )
            is None
        )

    def test_returns_none_for_a_missing_message_id(self, config):
        get = self.fake_get([{"storage": {"url": self.STORAGE_URL}}])
        assert (
            stored_message_mime(config, "", get=get, sleep=lambda s: None)
            is None
        )

    def test_waits_out_the_events_api_lag_before_giving_up(self, config):
        # The Events API can lag reception by well over a few seconds;
        # the lookup must keep polling for a minute or two (via the
        # injected sleep) rather than bounce to Mailgun's much slower
        # redelivery cycle.
        slept = []
        get = self.fake_get([])
        assert (
            stored_message_mime(
                config, "<m1@eve.gd>", get=get, sleep=slept.append
            )
            is None
        )
        assert 60 <= sum(slept) <= 300

    def test_retries_the_lookup_before_giving_up(self, config):
        calls = []

        def get(url, **kwargs):
            if "/events" in url:
                calls.append(url)
                if len(calls) < 3:
                    return FakeResponse(payload={"items": []})
                return FakeResponse(
                    payload={"items": [{"storage": {"url": self.STORAGE_URL}}]}
                )
            return FakeResponse(payload={"body-mime": "RAW MIME BYTES"})

        assert (
            stored_message_mime(
                config, "<m1@eve.gd>", get=get, sleep=lambda s: None
            )
            == b"RAW MIME BYTES"
        )
