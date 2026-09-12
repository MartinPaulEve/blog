#!/usr/bin/env bash
#
# thought.sh — post a short thought (wraps the thought_composer app).
# Opens an interactive composer with a live Bluesky character count
# (300 graphemes); Enter posts, Alt+Enter inserts a newline, Ctrl+P
# pastes an image from the clipboard, Ctrl+C cancels. The thought is
# stored untouched in _data/thoughts.yml (feeding /thoughts/, the post
# sidebar and the homepage), cross-posted to Bluesky and Mastodon
# (threading automatically when it runs long), and shipped with the
# quick deploy (jekyll build + rsync only — no Sequoia, no git work).
#
#   ./thought.sh                        # compose, post, quick-deploy
#   ./thought.sh --image shot.png       # attach an image (repeatable)
#   ./thought.sh --text "..."           # skip the composer
#   ./thought.sh --dry-run --text "…"   # show how it would thread
#   ./thought.sh --no-post              # blog only, no syndication
#   ./thought.sh --no-deploy            # do not build/rsync afterwards
#   ./thought.sh probe                  # check both services' credentials
#   ./thought.sh import-bluesky --dry-run  # preview a Bluesky back-import
#   ./thought.sh import-bluesky            # back-import old Bluesky posts
#   ./thought.sh import-twitter ARCHIVE    # back-import an X/Twitter archive (ZIP or folder)
#
# Needs BLUESKY_APP_PASSWORD and MASTODON_ACCESS_TOKEN in .env (see
# thought_composer/README.md for where to create them).

cd "$(dirname "$0")"

case "${1:-}" in
    probe)
        shift
        exec uv run --env-file .env --project thought_composer thought-probe "$@"
        ;;
    import-bluesky)
        shift
        exec uv run --env-file .env --project thought_composer thought-import-bluesky "$@"
        ;;
    import-twitter)
        shift
        exec uv run --env-file .env --project thought_composer thought-import-twitter "$@"
        ;;
    help | -h | --help)
        sed -n 's/^#   \([^ ].*\)/\1/p' "$0"
        exit 0
        ;;
    *)
        exec uv run --env-file .env --project thought_composer thought "$@"
        ;;
esac
