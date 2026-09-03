#!/usr/bin/env bash
#
# human.sh — manage the site's human.json vouches (wraps _human/human_json.py).
# See https://codeberg.org/robida/human.json for the format. Commands:
#
#   ./human.sh add domain.com     # vouch for a site (refuses duplicates)
#   ./human.sh revoke domain.com  # withdraw a vouch
#   ./human.sh renew domain.com   # refresh a vouch's date to today
#   ./human.sh list               # show current vouches
#
# Sites may be bare domains (kfitz.info) or full URLs. Dates default to
# today; pass --date YYYY-MM-DD to override. Exits non-zero when nothing
# changed (duplicate add, unknown revoke/renew).

cd "$(dirname "$0")"

usage() {
    sed -n 's/^#   \([^ ].*\)/\1/p' "$0"
    exit "${1:-2}"
}

case "${1:-}" in
    add | revoke | renew | list)
        exec uv run _human/human_json.py "$@"
        ;;
    help | -h | --help | "")
        usage 0
        ;;
    *)
        echo "Unknown command: $1" >&2
        usage
        ;;
esac
