#!/usr/bin/env bash
#
# meet.sh — mint links for the /meet video-call page (wraps _meet/meet.py).
# Signs JaaS tokens with the private key named by JAAS_PRIVATE_KEY_FILE in
# .env, then prints a private HOST link (moderator token) and a shareable
# GUEST link (non-moderator token for the same room). Both tokens ride in
# the URL fragment. With "Allow meeting participants to join
# unauthenticated" switched OFF in the JaaS console, nobody can open or
# enter a room without one of these links. Commands:
#
#   ./meet.sh new                  # random room: prints host + guest links
#   ./meet.sh new --room NAME      # stable room name for a recurring call
#   ./meet.sh new --hours N        # token lifetime (default 8, max 24)
#   ./meet.sh new --open           # also open the host link in the browser
#   ./meet.sh guest-link ROOM      # mint a fresh guest link for a room
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
