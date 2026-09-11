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
#   ./biron.sh update --dry-run                       # list changed posts
#   ./biron.sh update                                 # replace their records in place
#
# Deposits are created live in the archive (collection discovered from
# the service document; override with $BIRON_COLLECTION or --collection)
# and the biron: front-matter key is stamped into the post immediately.
# `update` replaces a changed post's record in place — same eprintid,
# same URL — since EPrints has no versioning; staleness is detected via
# the content hashes in _biron/shipped.yml (posts deposited before this
# pipeline are baselined as current on first run, never rewritten).
# _biron/deposited.yml tracks any deposit parked in review;
# _biron/skip.yml lists posts never to deposit. evedeploy runs backfill
# and update automatically at the end of every deploy.
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
    update)
        exec uv run --env-file .env --project biron_uploader biron-update "$@"
        ;;
    -h|--help|help)
        usage 0
        ;;
    *)
        usage
        ;;
esac
