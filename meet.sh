#!/usr/bin/env bash
#
# meet.sh — mint links for the /meet video-call page (wraps _meet/meet.py).
# Signs a JaaS moderator token with the private key named by
# JAAS_PRIVATE_KEY_FILE in .env, then prints a private HOST link (token in
# the URL fragment) and a shareable GUEST link (random room name only).
# Guests who arrive before the host wait on 8x8's "waiting for a
# moderator" screen, so nobody can start a call without the key. Commands:
#
#   ./meet.sh new                  # random room: prints host + guest links
#   ./meet.sh new --room NAME      # stable room name for a recurring call
#   ./meet.sh new --hours N        # host token lifetime (default 8, max 24)
#   ./meet.sh new --open           # also open the host link in the browser
#   ./meet.sh guest-link ROOM      # reprint the guest link for a room
#
# Tenant settings (AppID, key ID, display name) live in _data/meet.yml.

cd "$(dirname "$0")"

usage() {
    sed -n 's/^#   \([^ ].*\)/\1/p' "$0"
    exit "${1:-2}"
}

case "${1:-}" in
    new | guest-link)
        exec uv run --env-file .env --with pyyaml --with pyjwt --with cryptography _meet/meet.py "$@"
        ;;
    help | -h | --help | "")
        usage 0
        ;;
    *)
        echo "Unknown command: $1" >&2
        usage
        ;;
esac
