#!/usr/bin/env bash
#
# biron.sh — driver for BIROn (Birkbeck ePrints) deposits of blog posts
# (wraps the biron_uploader app). Run after a real deploy so the attached
# PDF is the final built edition. Commands:
#
#   ./biron.sh login                                  # browser sign-in, store cookie
#   ./biron.sh login --headless                       # silent cookie refresh
#   ./biron.sh probe                                  # check credentials
#   ./biron.sh dry-run _posts/YYYY-MM-DD-slug.md      # record summary, no network
#   ./biron.sh deposit _posts/YYYY-MM-DD-slug.md      # deposit one post
#   ./biron.sh backfill --dry-run                     # list posts not deposited
#   ./biron.sh backfill                               # deposit them all
#
# Deposits go to the SWORD inbox (override with $BIRON_COLLECTION or
# --collection) and await the repository's review workflow; the biron:
# front-matter key is stamped later by the _biron fetch sweep once the
# record is live. _biron/deposited.yml tracks in-flight deposits so they
# are not resent; _biron/skip.yml lists posts never to deposit.
#
# BIROn's auth is Microsoft SSO (Shibboleth), and its session cookie
# never touches the browser's on-disk store — so `login` drives a
# dedicated Chromium profile: sign in once interactively and the cookie
# lands in .biron_cookie (gitignored). Afterwards the persisted
# Microsoft session usually renews it SILENTLY: probe/deposit/backfill
# detect a stale cookie and re-harvest headlessly on their own; `login
# --headless` does the same by hand. Set BIRON_COOKIE=auto in .env so
# the evedeploy step knows deposits are configured (a literal cookie
# value still works as a manual override, and BIRON_USERNAME/
# BIRON_PASSWORD Basic auth remains supported if the systems team ever
# enables it).

cd "$(dirname "$0")"

usage() {
    sed -n 's/^#   \([^ ].*\)/\1/p' "$0"
    exit "${1:-2}"
}

cmd="${1:-}"
shift || true

case "$cmd" in
    login)
        exec uv run --env-file .env --project biron_uploader biron-login "$@"
        ;;
    probe)
        exec uv run --env-file .env --project biron_uploader biron-probe "$@"
        ;;
    dry-run)
        exec uv run --env-file .env --project biron_uploader biron-upload --dry-run "$@"
        ;;
    deposit)
        exec uv run --env-file .env --project biron_uploader biron-upload "$@"
        ;;
    backfill)
        exec uv run --env-file .env --project biron_uploader biron-backfill "$@"
        ;;
    -h|--help|help)
        usage 0
        ;;
    *)
        usage
        ;;
esac
