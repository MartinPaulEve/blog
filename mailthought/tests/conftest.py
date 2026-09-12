"""Shared fixtures: a Config on a temp data dir and a signed-form builder."""

import hashlib
import hmac
import time

import pytest

from mailthought.config import Config


@pytest.fixture
def config(tmp_path):
    return Config(
        allowed_senders=frozenset({"martin@eve.gd", "martin.eve@bbk.ac.uk"}),
        mailgun_api_key="key-testing",
        mailgun_signing_key="signing-secret",
        mailgun_domain="mg.eve.gd",
        mail_from="Thoughts <thoughts@mg.eve.gd>",
        mailgun_api_base="https://api.mailgun.net",
        require_auth=True,
        data_dir=tmp_path / "data",
    )


def sign(signing_key: str, timestamp: str, token: str) -> str:
    return hmac.new(
        signing_key.encode(), f"{timestamp}{token}".encode(), hashlib.sha256
    ).hexdigest()


def signed_fields(signing_key: str, token: str = "tok-0000000001") -> dict:
    """A valid Mailgun signature triple for "now"."""
    timestamp = str(int(time.time()))
    return {
        "timestamp": timestamp,
        "token": token,
        "signature": sign(signing_key, timestamp, token),
    }
