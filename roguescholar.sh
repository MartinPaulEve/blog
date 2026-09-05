#!/usr/bin/env bash
#
# roguescholar.sh — stamp Rogue Scholar record URLs into post front matter
# (wraps _identifiers/fetch_roguescholar.py). Rogue Scholar harvests the
# feed on a pull cycle, so run this a few minutes after deploy; --attempts
# keeps polling until the record appears. Also mirrors an atUri: line into
# atproto: when the post lacks one, so the AT Protocol page link renders.
#
#   ./roguescholar.sh _posts/YYYY-MM-DD-slug.md            # single lookup
#   ./roguescholar.sh --attempts 10 _posts/YYYY-MM-DD-slug.md   # poll ~20 min
#   ./roguescholar.sh --interval 60 --attempts 5 <post>    # custom cadence
#   ./roguescholar.sh --dry-run <post>                     # report only

cd "$(dirname "$0")"

exec uv run --with pyyaml --with certifi _identifiers/fetch_roguescholar.py "$@"
