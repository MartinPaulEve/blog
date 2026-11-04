"""Mint host and guest links for the /meet video-call page (JaaS / 8x8).

JaaS lets a tenant open a room only with an RS256 JWT signed by its
private key, and that key must never ship with a static site. So this
tool runs locally: it signs a moderator token, puts it in the URL
fragment of a host link (fragments never reach the server or its logs)
and prints a token-free guest link whose secret is the random room name.
The guest link carries a room-scoped non-moderator token of its own, so
the tenant can refuse unauthenticated joins outright and nobody can open
or enter a room without a link signed by the key.

Run through ./meet.sh, which supplies the uv incantation:

    ./meet.sh new [--room NAME] [--hours N] [--name "Name"] [--open]
    ./meet.sh guest-link ROOM
"""

import argparse
import datetime
import os
import re
import secrets
import shutil
import subprocess
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_FILE = os.path.join(ROOT, "_data", "meet.yml")
SITE_URL = "https://eve.gd"
MEET_PATH = "/meet/"
DEFAULT_HOURS = 8
MAX_HOURS = 24
ROOM_RE = re.compile(r"^[a-z0-9_-]{6,64}$")
PLACEHOLDER_KEY_ID = "REPLACE_WITH_KEY_ID"
PREMIUM_FEATURES = ("livestreaming", "recording", "transcription", "outbound-call")


class ConfigError(Exception):
    """A missing or unusable setting; the message says what to fix."""


def random_room():
    """Return a fresh lowercase room name with enough entropy to be a secret."""
    return secrets.token_hex(10)


def validate_room(name):
    """Return the room name as Jitsi will use it, or raise ValueError."""
    room = (name or "").strip().lower()
    if not ROOM_RE.match(room):
        raise ValueError(
            "room names are 6-64 characters of a-z, 0-9, '-' or '_' "
            f"(got {name!r})"
        )
    return room


def build_claims(app_id, room, host_name, now, hours, email=None, moderator=True):
    """Return the JaaS JWT payload for one specific room.

    A moderator token names the host; a guest token carries no identity
    at all, so each guest picks their own name on the prejoin screen.
    """
    hours = max(0, min(float(hours), MAX_HOURS))
    start = int(now.timestamp())
    user = {"moderator": "true" if moderator else "false"}
    if moderator:
        user["id"] = str(uuid.uuid4())
        user["name"] = host_name
        if email:
            user["email"] = email
    return {
        "aud": "jitsi",
        "iss": "chat",
        "sub": app_id,
        "room": room,
        "nbf": start - 60,
        "exp": start + int(hours * 3600),
        "context": {
            "user": user,
            "features": {feature: "false" for feature in PREMIUM_FEATURES},
        },
    }


def kid_for(app_id, key_id):
    """Return the JWT kid header: app_id/key_id.

    The JaaS console shows a key's ID already prefixed with the AppID and
    a slash, so accept that form too rather than doubling the prefix.
    """
    key_id = str(key_id).strip()
    prefix = app_id + "/"
    key_id = key_id.removeprefix(prefix)
    return f"{app_id}/{key_id}"


def sign(claims, private_key_pem, app_id, key_id):
    """Return the RS256-signed token with the tenant's kid header."""
    import jwt

    return jwt.encode(
        claims,
        private_key_pem,
        algorithm="RS256",
        headers={"kid": kid_for(app_id, key_id), "typ": "JWT"},
    )


def build_links(site_url, room, host_jwt=None, guest_jwt=None):
    """Return the guest link and, when a host token is given, the host link.

    Tokens ride in the fragment, which browsers never send to the server.
    """
    base = site_url.rstrip("/") + MEET_PATH + "#room=" + room
    links = {"guest": base, "host": None}
    if guest_jwt:
        links["guest"] = base + "&jwt=" + guest_jwt
    if host_jwt:
        links["host"] = base + "&jwt=" + host_jwt
        if guest_jwt:
            # So the host's page can show the guest link to share.
            links["host"] += "&guest=" + guest_jwt
    return links


def load_config(data_file, env):
    """Return tenant settings from the data file plus the private key PEM."""
    import yaml

    with open(data_file, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    for key in ("app_id", "key_id", "host_name"):
        if not data.get(key):
            raise ConfigError(f"{data_file} needs a {key} value")
    if str(data["key_id"]) == PLACEHOLDER_KEY_ID:
        raise ConfigError(
            f"set key_id in {data_file} to the API key ID from the JaaS console"
        )
    key_file = env.get("JAAS_PRIVATE_KEY_FILE")
    if not key_file:
        raise ConfigError(
            "JAAS_PRIVATE_KEY_FILE is not set in .env; point it at the JaaS private key (PEM)"
        )
    if not os.path.exists(key_file):
        raise ConfigError(f"private key file not found: {key_file}")
    with open(key_file, "rb") as f:
        private_key_pem = f.read()
    check_private_key(private_key_pem, key_file)
    return {
        "app_id": str(data["app_id"]),
        "key_id": str(data["key_id"]),
        "host_name": str(data["host_name"]),
        "host_email": data.get("host_email"),
        "private_key_pem": private_key_pem,
    }


def check_private_key(pem, key_file):
    """Raise ConfigError unless the bytes are a PEM private key.

    The JaaS console downloads the key as a .pk file; the extension is
    irrelevant, the contents must be PEM (BEGIN ... PRIVATE KEY).
    """
    from cryptography.hazmat.primitives import serialization

    try:
        serialization.load_pem_private_key(pem, password=None)
    except (ValueError, TypeError) as exc:
        raise ConfigError(
            f"{key_file} is not a PEM private key (expected a "
            "'-----BEGIN PRIVATE KEY-----' block, as downloaded from the JaaS console)"
        ) from exc


def copy_to_clipboard(text):
    """Put text on the clipboard if a known tool is around; report success."""
    for cmd in (["wl-copy"], ["xclip", "-selection", "clipboard"], ["pbcopy"]):
        if shutil.which(cmd[0]):
            try:
                # wl-copy forks a child that keeps serving the clipboard; it
                # must not inherit our stdout or anything piping this
                # script's output would wait on it forever.
                subprocess.run(
                    cmd, input=text.encode("utf-8"), check=True, timeout=5,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                return True
            except (subprocess.SubprocessError, OSError):
                return False
    return False


def open_in_browser(url):
    if shutil.which("xdg-open"):
        subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    return False


def build_parser():
    parser = argparse.ArgumentParser(prog="meet.sh", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new", help="start a call: mint a host link and a guest link")
    new.add_argument("--room", help="use this room name instead of a random one")
    new.add_argument("--hours", type=float, default=DEFAULT_HOURS,
                     help=f"host token lifetime in hours (default {DEFAULT_HOURS}, max {MAX_HOURS})")
    new.add_argument("--name", help="display name for the host (default from _data/meet.yml)")
    new.add_argument("--open", action="store_true", help="open the host link in the browser")

    guest = sub.add_parser("guest-link", help="mint a fresh guest link for an existing room")
    guest.add_argument("room")
    guest.add_argument("--hours", type=float, default=DEFAULT_HOURS,
                       help=f"guest token lifetime in hours (default {DEFAULT_HOURS}, max {MAX_HOURS})")
    return parser


def mint(cfg, room, hours, moderator, host_name=None):
    """Return (token, claims) for the room, as host or as guest."""
    now = datetime.datetime.now(datetime.UTC)
    claims = build_claims(
        cfg["app_id"], room, host_name or cfg["host_name"], now, hours,
        email=cfg.get("host_email"), moderator=moderator,
    )
    return sign(claims, cfg["private_key_pem"], cfg["app_id"], cfg["key_id"]), claims


def cmd_new(args, env, out):
    cfg = load_config(DATA_FILE, env)
    room = validate_room(args.room) if args.room else random_room()
    host_token, claims = mint(cfg, room, args.hours, moderator=True, host_name=args.name)
    guest_token, _ = mint(cfg, room, args.hours, moderator=False)
    links = build_links(SITE_URL, room, host_jwt=host_token, guest_jwt=guest_token)
    expires = datetime.datetime.fromtimestamp(claims["exp"], datetime.UTC)

    print(f"Room: {room}", file=out)
    print(f"Tokens valid until {expires:%Y-%m-%d %H:%M} UTC", file=out)
    print(f"Signed with kid {kid_for(cfg['app_id'], cfg['key_id'])}", file=out)
    print(file=out)
    print("GUEST link — share this with the people you want on the call:", file=out)
    print(f"  {links['guest']}", file=out)
    print(file=out)
    print("HOST link — keep private; it carries your moderator token:", file=out)
    print(f"  {links['host']}", file=out)
    print(file=out)
    if copy_to_clipboard(links["guest"]):
        print("(guest link copied to the clipboard)", file=out)
    if args.open:
        if open_in_browser(links["host"]):
            print("(host link opened in the browser)", file=out)
        else:
            print("(no xdg-open found; open the host link yourself)", file=out)
    return 0


def cmd_guest_link(args, env, out):
    cfg = load_config(DATA_FILE, env)
    room = validate_room(args.room)
    guest_token, claims = mint(cfg, room, args.hours, moderator=False)
    expires = datetime.datetime.fromtimestamp(claims["exp"], datetime.UTC)
    links = build_links(SITE_URL, room, guest_jwt=guest_token)
    print(f"Guest link for {room}, valid until {expires:%Y-%m-%d %H:%M} UTC:", file=out)
    print(f"  {links['guest']}", file=out)
    if copy_to_clipboard(links["guest"]):
        print("(copied to the clipboard)", file=out)
    return 0


def main(argv=None, env=None, out=None):
    env = os.environ if env is None else env
    out = sys.stdout if out is None else out
    args = build_parser().parse_args(argv)
    try:
        if args.command == "new":
            return cmd_new(args, env, out)
        return cmd_guest_link(args, env, out)
    except (ConfigError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
