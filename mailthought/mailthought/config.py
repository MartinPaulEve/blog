"""Environment-driven configuration for the gateway.

Everything the Python app needs arrives as environment variables (the
Coolify-managed contract in docker-compose.yml); SSH material and git
identity are the entrypoint's business, not ours. Missing required
values fail fast at startup rather than mid-email.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


class ConfigError(ValueError):
    """A required environment variable is missing or unusable."""


@dataclass(frozen=True)
class Config:
    allowed_senders: frozenset
    mailgun_api_key: str
    mailgun_signing_key: str
    mailgun_domain: str
    mail_from: str
    mailgun_api_base: str
    require_auth: bool
    data_dir: Path

    @property
    def blog_dir(self) -> Path:
        return self.data_dir / "blog"

    @property
    def drafts_dir(self) -> Path:
        return self.data_dir / "drafts"

    @property
    def inbox_dir(self) -> Path:
        return self.data_dir / "inbox"

    @property
    def state_dir(self) -> Path:
        return self.data_dir / "state"


def load_config(env: Mapping[str, str]) -> Config:
    """Build a Config from an environment mapping.

    ALLOWED_SENDERS is a comma-separated list, normalised to lowercase;
    an empty list is a configuration error (the gateway must never run
    open to the world). REQUIRE_AUTH accepts false/no/0 to disable the
    SPF/DKIM gate, anything else keeps it on.
    """
    required = {}
    for name in (
        "ALLOWED_SENDERS",
        "MAILGUN_API_KEY",
        "MAILGUN_SIGNING_KEY",
        "MAILGUN_DOMAIN",
        "MAIL_FROM",
    ):
        value = env.get(name, "").strip()
        if not value:
            raise ConfigError(f"{name} must be set")
        required[name] = value

    senders = frozenset(
        part.strip().lower()
        for part in required["ALLOWED_SENDERS"].split(",")
        if part.strip()
    )
    if not senders:
        raise ConfigError("ALLOWED_SENDERS must list at least one address")

    return Config(
        allowed_senders=senders,
        mailgun_api_key=required["MAILGUN_API_KEY"],
        mailgun_signing_key=required["MAILGUN_SIGNING_KEY"],
        mailgun_domain=required["MAILGUN_DOMAIN"],
        mail_from=required["MAIL_FROM"],
        mailgun_api_base=env.get(
            "MAILGUN_API_BASE", "https://api.mailgun.net"
        ).rstrip("/"),
        require_auth=env.get("REQUIRE_AUTH", "true").strip().lower()
        not in {"false", "no", "0"},
        data_dir=Path(env.get("DATA_DIR", "/data")),
    )
