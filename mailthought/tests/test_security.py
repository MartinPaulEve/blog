"""security: webhook signature, replay ledger, allowlist, SPF/DKIM verdicts."""

import json

import dkim
from conftest import sign

from mailthought.security import (
    MimeStash,
    SeenLedger,
    auth_results,
    content_bound,
    dkim_authenticated,
    is_authenticated,
    retrieval_curl,
    sender_address,
    sender_allowed,
    storage_candidates,
    stored_message_mime,
    verification_mime,
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


class TestMimeStash:
    """Local raw-MIME copies delivered by the route's mime forward."""

    RAW = b"From: martin@eve.gd\r\nMessage-Id: <m1@eve.gd>\r\n\r\nhi\r\n"

    def test_round_trips_raw_mime(self, tmp_path):
        stash = MimeStash(tmp_path / "mime")
        stash.save("<m1@eve.gd>", self.RAW)
        assert stash.load("<m1@eve.gd>") == self.RAW

    def test_angle_brackets_do_not_change_the_key(self, tmp_path):
        stash = MimeStash(tmp_path / "mime")
        stash.save("<m1@eve.gd>", self.RAW)
        assert stash.load("m1@eve.gd") == self.RAW

    def test_unknown_message_id_loads_none(self, tmp_path):
        stash = MimeStash(tmp_path / "mime")
        assert stash.load("<missing@eve.gd>") is None

    def test_expired_copies_are_gone(self, tmp_path):
        stash = MimeStash(tmp_path / "mime", ttl_seconds=100)
        stash.save("<m1@eve.gd>", self.RAW, now=1000.0)
        assert stash.load("<m1@eve.gd>", now=2000.0) is None

    def test_hostile_message_ids_cannot_escape_the_directory(self, tmp_path):
        stash = MimeStash(tmp_path / "mime")
        stash.save("../../evil", self.RAW)
        assert stash.load("../../evil") == self.RAW
        outside = [
            path
            for path in tmp_path.rglob("*")
            if path.is_file() and (tmp_path / "mime") not in path.parents
        ]
        assert outside == []


class TestMimeStashFirstWriteWins:
    """A Message-Id's first raw copy must survive later, differing
    deliveries — otherwise a forger could replace the genuine copy
    after it arrives."""

    RAW = b"From: martin@eve.gd\r\n\r\ngenuine\r\n"
    FORGED = b"From: martin@eve.gd\r\n\r\nforged\r\n"

    def test_a_differing_second_copy_does_not_replace_the_first(
        self, tmp_path
    ):
        stash = MimeStash(tmp_path / "mime")
        stash.save("<m1@eve.gd>", self.RAW, now=1000.0)
        stash.save("<m1@eve.gd>", self.FORGED, now=1001.0)
        assert stash.load("<m1@eve.gd>", now=1002.0) == self.RAW

    def test_an_identical_redelivery_is_harmless(self, tmp_path):
        stash = MimeStash(tmp_path / "mime")
        stash.save("<m1@eve.gd>", self.RAW, now=1000.0)
        stash.save("<m1@eve.gd>", self.RAW, now=1001.0)
        assert stash.load("<m1@eve.gd>", now=1002.0) == self.RAW

    def test_the_stash_is_capped_dropping_the_oldest(self, tmp_path):
        stash = MimeStash(tmp_path / "mime", max_files=2)
        stash.save("<a@eve.gd>", self.RAW, now=1000.0)
        stash.save("<b@eve.gd>", self.RAW, now=1001.0)
        stash.save("<c@eve.gd>", self.RAW, now=1002.0)
        assert stash.load("<a@eve.gd>", now=1003.0) is None
        assert stash.load("<b@eve.gd>", now=1003.0) == self.RAW
        assert stash.load("<c@eve.gd>", now=1003.0) == self.RAW


def mime_message(
    sender="Martin Eve <martin@eve.gd>",
    text="a thought",
    image: bytes | None = None,
) -> bytes:
    """A small multipart message shaped like real inbound mail."""
    from email.mime.image import MIMEImage
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = "thought@mg.eve.gd"
    message["Message-Id"] = "<m1@eve.gd>"
    message.attach(MIMEText(text, "plain"))
    if image is not None:
        attachment = MIMEImage(image, "jpeg")
        attachment.add_header(
            "Content-Disposition", "attachment", filename="gate.jpg"
        )
        message.attach(attachment)
    return message.as_bytes()


class TestContentBound:
    """The verified raw message must be the message being published."""

    IMG = b"\xff\xd8JPGBYTES"

    def test_matching_sender_text_and_image_bind(self):
        raw = mime_message(image=self.IMG)
        assert content_bound(
            raw, "martin@eve.gd", "a thought", [self.IMG]
        ) is True

    def test_a_different_from_address_does_not_bind(self):
        raw = mime_message(sender="Mallory <mallory@evil.example>")
        assert content_bound(raw, "martin@eve.gd", "a thought", []) is False

    def test_text_absent_from_the_message_does_not_bind(self):
        raw = mime_message(text="something else entirely")
        assert content_bound(raw, "martin@eve.gd", "a thought", []) is False

    def test_an_image_absent_from_the_message_does_not_bind(self):
        raw = mime_message(image=self.IMG)
        assert content_bound(
            raw, "martin@eve.gd", "a thought", [b"OTHER BYTES"]
        ) is False

    def test_job_text_may_be_a_trimmed_prefix_of_the_body(self):
        # Alt directives and signatures are stripped from the job text;
        # whitespace is reflowed. The remainder must still bind.
        raw = mime_message(
            text="a  thought\r\nwith lines\r\nalt: a red gate\r\n-- \r\nsig"
        )
        assert content_bound(
            raw, "martin@eve.gd", "a thought with lines", []
        ) is True

    def test_html_only_mail_binds_on_sender_and_attachments(self):
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        message = MIMEMultipart()
        message["From"] = "martin@eve.gd"
        message.attach(MIMEText("<p>a <b>thought</b></p>", "html"))
        assert content_bound(
            message.as_bytes(), "martin@eve.gd", "a thought", []
        ) is True

    def test_an_empty_raw_message_does_not_bind(self):
        assert content_bound(b"", "martin@eve.gd", "a thought", []) is False


class ArrivingStash:
    """A stash whose copy appears after a given number of load calls."""

    def __init__(self, raw: bytes, after: int):
        self.raw = raw
        self.after = after
        self.calls = 0

    def load(self, message_id, now=None):
        self.calls += 1
        return self.raw if self.calls > self.after else None


class TestVerificationMime:
    """Local stash first; Mailgun's storage API only as a fallback."""

    RAW = b"From: martin@eve.gd\r\n\r\nhi\r\n"

    def test_returns_the_stashed_copy_without_waiting(self, config, tmp_path):
        stash = MimeStash(tmp_path / "mime")
        stash.save("<m1@eve.gd>", self.RAW)
        slept = []
        assert (
            verification_mime(
                config, "<m1@eve.gd>", stash=stash, sleep=slept.append
            )
            == self.RAW
        )
        assert slept == []

    def test_waits_for_a_copy_that_arrives_late(self, config):
        stash = ArrivingStash(self.RAW, after=3)
        assert (
            verification_mime(
                config, "<m1@eve.gd>", stash=stash, sleep=lambda s: None
            )
            == self.RAW
        )

    def test_falls_back_to_the_storage_api(self, config, tmp_path):
        storage_url = TestStoredMessageMime.STORAGE_URL

        def get(url, **kwargs):
            if "/events" in url:
                return FakeResponse(
                    payload={"items": [{"storage": {"url": storage_url}}]}
                )
            return FakeResponse(payload={"body-mime": "RAW MIME BYTES"})

        assert (
            verification_mime(
                config, "<m1@eve.gd>",
                stash=MimeStash(tmp_path / "mime"),
                attempts=2, sleep=lambda s: None, get=get,
            )
            == b"RAW MIME BYTES"
        )

    def test_returns_none_when_nothing_ever_arrives(self, config, tmp_path):
        def get(url, **kwargs):
            return FakeResponse(status_code=404, payload={"items": []})

        assert (
            verification_mime(
                config, "<m1@eve.gd>",
                stash=MimeStash(tmp_path / "mime"),
                attempts=2, sleep=lambda s: None, get=get,
            )
            is None
        )


class TestRetrievalCurl:
    """The copy-pasteable curl command logged for manual retrieval."""

    URL = (
        "https://storage-europe-west1.api.mailgun.net/v3/domains/"
        "mg.eve.gd/messages/KEY123"
    )

    def test_command_fetches_the_given_url_as_raw_mime(self):
        command = retrieval_curl(self.URL)
        assert command.startswith("curl")
        assert self.URL in command
        assert "Accept: message/rfc2822" in command

    def test_command_authenticates_without_embedding_the_key(self):
        command = retrieval_curl(self.URL)
        assert "api:$MAILGUN_API_KEY" in command
        assert "key-" not in command


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

    def test_forward_only_routes_have_no_stored_events(self, config):
        # A forward()-only route never emits a "stored" event — the
        # storage block rides on accepted/failed events instead — so
        # the lookup must not restrict the search by event type. This
        # fake models real Mailgun behaviour for such routes: an
        # event-filtered query finds nothing.
        def get(url, **kwargs):
            if "/events" in url:
                params = kwargs.get("params") or {}
                if "event" in params:
                    return FakeResponse(payload={"items": []})
                return FakeResponse(
                    payload={
                        "items": [
                            {
                                "event": "failed",
                                "storage": {"url": [self.STORAGE_URL]},
                            }
                        ]
                    }
                )
            if url == self.STORAGE_URL:
                return FakeResponse(payload={"body-mime": "RAW MIME BYTES"})
            return FakeResponse(status_code=404)

        assert (
            stored_message_mime(
                config, "<m1@eve.gd>", get=get, sleep=lambda s: None
            )
            == b"RAW MIME BYTES"
        )

    def test_storage_url_may_be_a_list(self, config):
        # failed events carry storage.url as a list of URLs; stored
        # events carry a plain string. Both shapes must work.
        get = self.fake_get([{"storage": {"url": [self.STORAGE_URL]}}])
        assert (
            stored_message_mime(
                config, "<m1@eve.gd>", get=get, sleep=lambda s: None
            )
            == b"RAW MIME BYTES"
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

    def test_candidates_pair_event_types_with_urls(self):
        items = [
            {"event": "accepted", "storage": {"url": self.STORAGE_URL}},
            {"event": "failed", "storage": {"url": [self.STORAGE_URL, ""]}},
            {"event": "delivered"},
        ]
        assert storage_candidates(items) == [
            ("accepted", self.STORAGE_URL),
            ("failed", self.STORAGE_URL),
        ]

    def test_candidates_tolerate_a_missing_event_type(self):
        assert storage_candidates([{"storage": {"url": self.STORAGE_URL}}]) == [
            ("?", self.STORAGE_URL)
        ]

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
