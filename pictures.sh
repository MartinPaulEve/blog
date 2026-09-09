#!/usr/bin/env bash
#
# pictures.sh — manage the /pictures re-use page (wraps _pictures/manage.py).
# Each entry pairs an image with a description and a suggested credit line;
# add renders a web-sized preview into images/pictures-previews/. Commands:
#
#   ./pictures.sh add              # walk through adding an image
#   ./pictures.sh edit [file]      # amend a description or credit line
#   ./pictures.sh remove [file]    # take an image off the page
#   ./pictures.sh list             # show current entries
#
# add/edit prompt for anything not given as --file/--description/--credit
# flags; remove asks before acting (pass --yes to skip). File names may be
# bare (02.png, resolved against images/) or site-absolute (/images/02.png).

cd "$(dirname "$0")"

usage() {
    sed -n 's/^#   \([^ ].*\)/\1/p' "$0"
    exit "${1:-2}"
}

case "${1:-}" in
    add | edit | remove | list)
        exec uv run --with pyyaml --with pillow _pictures/manage.py "$@"
        ;;
    help | -h | --help | "")
        usage 0
        ;;
    *)
        echo "Unknown command: $1" >&2
        usage
        ;;
esac
