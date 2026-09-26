#!/usr/bin/env bash
#
# webmentions.sh — driver for outgoing webmentions (wraps
# _webmentions/send_webmentions.py). Run from the blog root, after a build so
# it reads the current _site. Commands:
#
#   ./webmentions.sh pending     # list what WOULD be sent, and why (no sends)
#   ./webmentions.sh send        # discover endpoints and send for real
#   ./webmentions.sh baseline    # record current posts as sent, sending nothing
#   ./webmentions.sh pending --only-thoughts   # short thoughts only (any cmd)
#
# `pending` (the default) is offline and safe: it just diffs the built _site
# against the sent ledger (_webmentions/sent.json) and prints the plan with a
# per-reason breakdown. `send` needs network access and is what the deploy
# pipeline runs automatically; `baseline` seeds the ledger without sending
# (used once at set-up). Extra flags pass straight through — notably
# --only-thoughts, which restricts a pass to the short thoughts on the
# /thoughts/<YYYY-MM>/ pages (the quick deploy after a thought runs exactly
# that, so a thought that links somewhere mentions it within seconds).

cd "$(dirname "$0")"

cmd="${1:-pending}"
shift || true

case "$cmd" in
    pending)
        exec uv run _webmentions/send_webmentions.py --dry-run "$@"
        ;;
    send)
        exec uv run _webmentions/send_webmentions.py "$@"
        ;;
    baseline)
        exec uv run _webmentions/send_webmentions.py --baseline "$@"
        ;;
    help | -h | --help | "")
        sed -n 's/^#   \([^ ].*\)/\1/p' "$0"
        exit 0
        ;;
    *)
        echo "Unknown command: $cmd" >&2
        sed -n 's/^#   \([^ ].*\)/\1/p' "$0"
        exit 2
        ;;
esac
