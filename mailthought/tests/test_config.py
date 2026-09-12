"""load_config: the environment contract, validated at startup."""

from pathlib import Path

import pytest

from mailthought.config import ConfigError, load_config

FULL_ENV = {
    "ALLOWED_SENDERS": "Martin@eve.gd, martin.eve@bbk.ac.uk",
    "MAILGUN_API_KEY": "key-abc",
    "MAILGUN_SIGNING_KEY": "whsec",
    "MAILGUN_DOMAIN": "mg.eve.gd",
    "MAIL_FROM": "Thoughts <thoughts@mg.eve.gd>",
}


def test_full_environment_parses():
    config = load_config(FULL_ENV)
    assert config.allowed_senders == frozenset(
        {"martin@eve.gd", "martin.eve@bbk.ac.uk"}
    )
    assert config.mailgun_api_key == "key-abc"
    assert config.mailgun_signing_key == "whsec"
    assert config.mailgun_domain == "mg.eve.gd"
    assert config.mail_from == "Thoughts <thoughts@mg.eve.gd>"


def test_defaults_when_optionals_absent():
    config = load_config(FULL_ENV)
    assert config.mailgun_api_base == "https://api.mailgun.net"
    assert config.require_auth is True
    assert config.data_dir == Path("/data")


def test_allowed_senders_lowercased_and_blank_entries_dropped():
    env = dict(FULL_ENV, ALLOWED_SENDERS=" A@B.COM ,, c@d.com , ")
    config = load_config(env)
    assert config.allowed_senders == frozenset({"a@b.com", "c@d.com"})


@pytest.mark.parametrize("missing", sorted(FULL_ENV))
def test_missing_required_variable_is_an_error(missing):
    env = {k: v for k, v in FULL_ENV.items() if k != missing}
    with pytest.raises(ConfigError):
        load_config(env)


def test_empty_allowlist_is_an_error():
    with pytest.raises(ConfigError):
        load_config(dict(FULL_ENV, ALLOWED_SENDERS="  , ,"))


@pytest.mark.parametrize("value", ["false", "False", "no", "0"])
def test_require_auth_can_be_disabled(value):
    config = load_config(dict(FULL_ENV, REQUIRE_AUTH=value))
    assert config.require_auth is False


@pytest.mark.parametrize("value", ["true", "yes", "1", "anything"])
def test_require_auth_stays_on_for_other_values(value):
    config = load_config(dict(FULL_ENV, REQUIRE_AUTH=value))
    assert config.require_auth is True


def test_data_dir_override_and_derived_directories():
    config = load_config(dict(FULL_ENV, DATA_DIR="/var/gateway"))
    assert config.data_dir == Path("/var/gateway")
    assert config.blog_dir == Path("/var/gateway/blog")
    assert config.drafts_dir == Path("/var/gateway/drafts")
    assert config.inbox_dir == Path("/var/gateway/inbox")
    assert config.state_dir == Path("/var/gateway/state")


def test_api_base_override_for_eu_region():
    config = load_config(dict(FULL_ENV, MAILGUN_API_BASE="https://api.eu.mailgun.net"))
    assert config.mailgun_api_base == "https://api.eu.mailgun.net"
