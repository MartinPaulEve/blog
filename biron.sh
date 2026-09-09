#!/usr/bin/env bash
#
# biron.sh — driver for BIROn (Birkbeck ePrints) deposits of blog posts
# (wraps the biron_uploader app). Run after a real deploy so the attached
# PDF is the final built edition. Commands:
#
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
# probe, deposit and backfill need BIRON_USERNAME and BIRON_PASSWORD in
# .env; dry-run does not.

cd "$(dirname "$0")"

usage() {
    sed -n 's/^#   \([^ ].*\)/\1/p' "$0"
    exit "${1:-2}"
}

cmd="${1:-}"
shift || true

case "$cmd" in
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
