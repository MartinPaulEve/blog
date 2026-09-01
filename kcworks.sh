#!/usr/bin/env bash
#
# kcworks.sh — driver for KC Works deposits of blog posts (wraps the
# kcworks_uploader app). Run after a real deploy so the attached PDF is the
# final built edition. Commands:
#
#   ./kcworks.sh dry-run _posts/YYYY-MM-DD-slug.md    # record JSON, no network
#   ./kcworks.sh deposit _posts/YYYY-MM-DD-slug.md    # draft (the default)
#   ./kcworks.sh deposit --live _posts/YYYY-MM-DD-slug.md   # publish now
#   ./kcworks.sh publish <uploads-url-or-record-id>   # publish a draft
#   ./kcworks.sh backfill --dry-run                   # list posts not deposited
#   ./kcworks.sh backfill                             # deposit+publish them all
#   ./kcworks.sh collection create --title "..."      # one-time: make it
#   ./kcworks.sh collection backfill                  # deposits -> collection
#   ./kcworks.sh collection logo <image>              # set collection icon
#
# Published records land in the collection named by kcworks_collection in
# _config.yml (opt out per run with --no-collection).
#
# Other kcworks-upload flags (--no-doi, --pdf PATH, --base-url URL, --token)
# pass straight through. deposit and publish need $KCWORKS_API_TOKEN (or
# --token); dry-run does not.
#
# Once a deposit is published, record it in the post's front matter:
#
#     kcworks: https://works.hcommons.org/records/<id>
#
# The signposting plugin emits that as archivedAt in the post's metadata.json,
# linking the blog and repository records in both directions.

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
