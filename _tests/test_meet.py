"""Behavioural tests for the /meet link minter (run from the blog root):

    uv run --with pyyaml --with pyjwt --with cryptography --with pytest -m pytest _tests/test_meet.py
"""

import datetime
import io
import pathlib
import re
import sys

import jwt as pyjwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "_meet"))

import meet

APP_ID = "vpaas-magic-cookie-0123456789abcdef0123456789abcdef"
KEY_ID = "abc123"
NOW = datetime.datetime(2026, 11, 4, 12, 0, tzinfo=datetime.UTC)
ROOM_RE = re.compile(r"^[a-z0-9_-]{6,64}$")


@pytest.fixture(scope="module")
def keypair():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public_pem = key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


class TestRandomRoom:
    def test_is_a_valid_lowercase_room_name(self):
        room = meet.random_room()
        assert ROOM_RE.match(room)
        assert room == room.lower()

    def test_is_long_enough_to_be_a_secret(self):
        assert len(meet.random_room()) >= 16

    def test_two_rooms_differ(self):
        assert meet.random_room() != meet.random_room()


class TestValidateRoom:
    def test_accepts_a_plain_name_and_lowercases_it(self):
        assert meet.validate_room("Family-Call") == "family-call"

    def test_strips_surrounding_whitespace(self):
        assert meet.validate_room("  weekly_call ") == "weekly_call"

    @pytest.mark.parametrize("bad", ["", "abc", "has space", "slash/room", "a" * 65, "*"])
    def test_rejects_names_that_would_not_survive_a_url(self, bad):
        with pytest.raises(ValueError):
            meet.validate_room(bad)


class TestBuildClaims:
    def claims(self, **kw):
        args = {"app_id": APP_ID, "room": "room-one", "host_name": "Martin", "now": NOW, "hours": 2}
        args.update(kw)
        return meet.build_claims(**args)

    def test_fixed_jaas_claims(self):
        c = self.claims()
        assert c["aud"] == "jitsi"
        assert c["iss"] == "chat"
        assert c["sub"] == APP_ID

    def test_room_is_the_specific_room_never_a_wildcard(self):
        assert self.claims()["room"] == "room-one"

    def test_host_is_moderator_with_display_name(self):
        user = self.claims()["context"]["user"]
        assert user["moderator"] == "true"
        assert user["name"] == "Martin"
        assert user["id"]

    def test_email_is_included_only_when_given(self):
        assert "email" not in self.claims()["context"]["user"]
        assert self.claims(email="m@example.org")["context"]["user"]["email"] == "m@example.org"

    def test_lifetime_matches_requested_hours(self):
        c = self.claims(hours=3)
        assert c["exp"] - c["nbf"] == pytest.approx(3 * 3600, abs=120)
        assert c["nbf"] <= int(NOW.timestamp())
        assert c["exp"] > int(NOW.timestamp())

    def test_hours_are_clamped_to_the_maximum(self):
        c = self.claims(hours=1000)
        assert c["exp"] - c["nbf"] <= meet.MAX_HOURS * 3600 + 120

    def test_premium_features_are_off(self):
        features = self.claims()["context"]["features"]
        assert features
        assert all(v == "false" for v in features.values())


class TestSign:
    def test_token_verifies_with_the_public_key(self, keypair):
        private_pem, public_pem = keypair
        claims = meet.build_claims(APP_ID, "room-one", "Martin", NOW, 2)
        token = meet.sign(claims, private_pem, APP_ID, KEY_ID)
        decoded = pyjwt.decode(
            token, public_pem, algorithms=["RS256"], audience="jitsi",
            options={"verify_exp": False, "verify_nbf": False},
        )
        assert decoded["room"] == "room-one"
        assert decoded["context"]["user"]["moderator"] == "true"

    def test_header_names_the_key(self, keypair):
        private_pem, _ = keypair
        claims = meet.build_claims(APP_ID, "room-one", "Martin", NOW, 2)
        header = pyjwt.get_unverified_header(meet.sign(claims, private_pem, APP_ID, KEY_ID))
        assert header["alg"] == "RS256"
        assert header["kid"] == f"{APP_ID}/{KEY_ID}"
        assert header["typ"] == "JWT"

    def test_token_from_the_wrong_key_does_not_verify(self, keypair):
        private_pem, _ = keypair
        other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        other_pub = other.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        claims = meet.build_claims(APP_ID, "room-one", "Martin", NOW, 2)
        token = meet.sign(claims, private_pem, APP_ID, KEY_ID)
        with pytest.raises(pyjwt.InvalidSignatureError):
            pyjwt.decode(token, other_pub, algorithms=["RS256"], audience="jitsi",
                         options={"verify_exp": False})


class TestBuildLinks:
    def test_guest_link_carries_only_the_room_in_the_fragment(self):
        links = meet.build_links("https://eve.gd", "room-one")
        assert links["guest"] == "https://eve.gd/meet/#room=room-one"

    def test_host_link_adds_the_token_to_the_fragment(self):
        links = meet.build_links("https://eve.gd", "room-one", jwt="TOKEN")
        assert links["host"] == "https://eve.gd/meet/#room=room-one&jwt=TOKEN"
        assert links["guest"] == "https://eve.gd/meet/#room=room-one"

    def test_no_host_link_without_a_token(self):
        assert meet.build_links("https://eve.gd", "room-one").get("host") is None

    def test_nothing_goes_in_the_query_string(self):
        links = meet.build_links("https://eve.gd/", "room-one", jwt="TOKEN")
        assert "?" not in links["host"]
        assert "?" not in links["guest"]
        assert "//meet" not in links["guest"]


class TestLoadConfig:
    def write_data(self, tmp_path, **overrides):
        data = {"app_id": APP_ID, "key_id": KEY_ID, "host_name": "Martin"}
        data.update(overrides)
        path = tmp_path / "meet.yml"
        path.write_text("\n".join(f"{k}: {v}" for k, v in data.items()), encoding="utf-8")
        return path

    def test_reads_tenant_settings_and_private_key(self, tmp_path, keypair):
        private_pem, _ = keypair
        key_file = tmp_path / "jaas.pem"
        key_file.write_bytes(private_pem)
        cfg = meet.load_config(self.write_data(tmp_path), {"JAAS_PRIVATE_KEY_FILE": str(key_file)})
        assert cfg["app_id"] == APP_ID
        assert cfg["key_id"] == KEY_ID
        assert cfg["host_name"] == "Martin"
        assert cfg["private_key_pem"] == private_pem

    def test_missing_key_setting_is_a_clear_error(self, tmp_path):
        with pytest.raises(meet.ConfigError, match="JAAS_PRIVATE_KEY_FILE"):
            meet.load_config(self.write_data(tmp_path), {})

    def test_missing_key_file_is_a_clear_error(self, tmp_path):
        with pytest.raises(meet.ConfigError, match="jaas.pem"):
            meet.load_config(self.write_data(tmp_path), {"JAAS_PRIVATE_KEY_FILE": str(tmp_path / "jaas.pem")})

    def test_placeholder_key_id_is_a_clear_error(self, tmp_path, keypair):
        private_pem, _ = keypair
        key_file = tmp_path / "jaas.pem"
        key_file.write_bytes(private_pem)
        data = self.write_data(tmp_path, key_id="REPLACE_WITH_KEY_ID")
        with pytest.raises(meet.ConfigError, match="key_id"):
            meet.load_config(data, {"JAAS_PRIVATE_KEY_FILE": str(key_file)})


class TestCli:
    @pytest.fixture
    def env(self, tmp_path, keypair, monkeypatch):
        private_pem, public_pem = keypair
        key_file = tmp_path / "jaas.pem"
        key_file.write_bytes(private_pem)
        data = tmp_path / "meet.yml"
        data.write_text(f"app_id: {APP_ID}\nkey_id: {KEY_ID}\nhost_name: Martin\n", encoding="utf-8")
        monkeypatch.setattr(meet, "DATA_FILE", str(data))
        monkeypatch.setattr(meet, "copy_to_clipboard", lambda text: False)
        return {"JAAS_PRIVATE_KEY_FILE": str(key_file), "_public_pem": public_pem}

    def run(self, argv, env):
        out = io.StringIO()
        code = meet.main(argv, env={k: v for k, v in env.items() if not k.startswith("_")}, out=out)
        return code, out.getvalue()

    def test_new_prints_a_host_and_a_guest_link(self, env):
        code, text = self.run(["new", "--room", "family-call", "--hours", "2"], env)
        assert code == 0
        host = re.search(r"https://eve\.gd/meet/#room=family-call&jwt=(\S+)", text)
        assert host
        assert "https://eve.gd/meet/#room=family-call" in text
        decoded = pyjwt.decode(host.group(1), env["_public_pem"], algorithms=["RS256"], audience="jitsi")
        assert decoded["room"] == "family-call"
        assert decoded["context"]["user"]["moderator"] == "true"

    def test_new_without_room_mints_a_random_one(self, env):
        code, text = self.run(["new"], env)
        assert code == 0
        rooms = set(re.findall(r"#room=([a-z0-9_-]+)", text))
        assert len(rooms) == 1
        assert ROOM_RE.match(rooms.pop())

    def test_guest_link_needs_no_key(self, env, tmp_path):
        code, text = self.run(["guest-link", "family-call"], {"JAAS_PRIVATE_KEY_FILE": str(tmp_path / "missing.pem")})
        assert code == 0
        assert "https://eve.gd/meet/#room=family-call" in text
        assert "jwt=" not in text

    def test_bad_room_name_fails_cleanly(self, env):
        code, _ = self.run(["new", "--room", "has space"], env)
        assert code != 0
