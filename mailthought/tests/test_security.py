"""security: webhook signature, replay ledger, allowlist, SPF/DKIM verdicts."""

import json

from conftest import sign

from mailthought.security import (
    SeenLedger,
    auth_results,
    is_authenticated,
    sender_address,
    sender_allowed,
    verify_signature,
)

KEY = "signing-secret"


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
