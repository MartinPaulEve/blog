#!/usr/bin/env bash
#
# kcworks.sh — driver for KC Works deposits of blog posts (wraps the
# kcworks_uploader app, which uses KC Works' streamlined import API: one
# request creates, publishes and collects a work with its files). Run
# after a real deploy so the attached PDF is the final built edition.
# Commands:
#
#   ./kcworks.sh dry-run _posts/YYYY-MM-DD-slug.md    # record JSON, no network
#   ./kcworks.sh deposit _posts/YYYY-MM-DD-slug.md    # import, publish, stamp
#   ./kcworks.sh update --dry-run                     # list stale deposits
#   ./kcworks.sh update                               # re-import them
#   ./kcworks.sh backfill --dry-run                   # list posts not deposited
#   ./kcworks.sh backfill                             # deposit them all
#   ./kcworks.sh publish <uploads-url-or-record-id>   # publish a hand-made draft
#   ./kcworks.sh collection create --title "..."      # one-time: make it
#   ./kcworks.sh collection backfill                  # deposits -> collection
#   ./kcworks.sh collection logo <image>              # set collection icon
#
# Deposits are imported straight into the collection named by
# kcworks_collection in _config.yml (override per run with --collection);
# there is no draft stage, so a deposit is live when the command returns.
#
# Other kcworks-upload flags (--no-doi, --pdf PATH, --base-url URL, --token)
# pass straight through. Everything but dry-run needs $KCWORKS_API_TOKEN
# (or --token), and the token's user must curate the collection.
#
# deposit, backfill and update stamp the published record URL into the
# post's front matter automatically:
#
#     kcworks: https://works.hcommons.org/records/<id>
#
# After `publish` (which takes a record id, not a post path), add that
# line by hand. The signposting plugin emits it as archivedAt in the
# post's metadata.json, linking the blog and repository records in both
# directions.

cd "$(dirname "$0")"

usage() {
    sed -n 's/^#   \([^ ].*\)/\1/p' "$0"
    exit "${1:-2}"
}

cmd="${1:-}"
shift || true

case "$cmd" in
    dry-run)
        exec uv run --env-file .env --project kcworks_uploader kcworks-upload --dry-run "$@"
        ;;
    deposit)
        exec uv run --env-file .env --project kcworks_uploader kcworks-upload "$@"
        ;;
    publish)
        exec uv run --env-file .env --project kcworks_uploader kcworks-publish "$@"
        ;;
    backfill)
        exec uv run --env-file .env --project kcworks_uploader kcworks-backfill "$@"
        ;;
    update)
        exec uv run --env-file .env --project kcworks_uploader kcworks-update "$@"
        ;;
    collection)
        exec uv run --env-file .env --project kcworks_uploader kcworks-collection "$@"
        ;;
    help | -h | --help | "")
        usage 0
        ;;
    *)
        echo "Unknown command: $cmd" >&2
        usage
        ;;
esac
