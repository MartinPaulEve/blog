#!/usr/bin/env bash
#
# publish.sh — resize covers, build the Jekyll site, preview the Sequoia
# (ATProto) publish, confirm, then publish + commit + push.
#
# Keep this at your blog root (next to sequoia.json) and run it from there:
#   ./publish.sh ["commit message"]
#   ./publish.sh --no-resize ["commit message"]
#
set -euo pipefail

# --- options ---
RESIZE=1
if [ "${1:-}" = "--no-resize" ]; then
    RESIZE=0
    shift
fi
MSG="${1:-Publish $(date '+%Y-%m-%d %H:%M')}"

# --- run from the script's own directory (your blog root) ---
cd "$(dirname "$0")"

# --- preflight ---
command -v sequoia >/dev/null || { echo "sequoia not found on PATH" >&2; exit 1; }
# The Nix-packaged sequoia wraps its own Node 24, so a PATH node is optional;
# only enforce the minimum version if one is present (e.g. npm-installed sequoia).
if command -v node >/dev/null; then
    node_major=$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)
    if [ "$node_major" -lt 19 ]; then
        echo "Node $(node -v 2>/dev/null || echo '?') detected; sequoia needs Node >= 19." >&2
        echo "Switch to Node >= 19 first, then re-run." >&2
        exit 1
    fi
fi

# --- 1. resize oversized cover images (idempotent; skips ones already small) ---
if [ "$RESIZE" -eq 1 ] && [ -f ./resize_covers.py ]; then
    echo "==> Checking cover image sizes"
    uv run --with pillow --with python-frontmatter ./resize_covers.py
fi

# --- 2. dry-run preview (no writes) ---
echo "==> Sequoia dry run — nothing is published yet"
sequoia publish --dry-run

# --- 3. confirmation gate ---
echo
read -r -p "Publish these to ATProto for real? [y/N] " reply </dev/tty || reply=""
case "$reply" in
    [yY] | [yY][eE][sS]) ;;
    *)
        echo "Aborted — nothing published. Local build/resize changes are left uncommitted."
        exit 0
        ;;
esac

# --- 4. real publish ---
echo "==> Publishing to ATProto"
sequoia publish

# --- 5. refresh CV files from eprintsToCV output (sibling repo) ---
CV_SRC="../eprintsToCV/output"
if [ -f "$CV_SRC/martin_paul_eve.pdf" ] && [ -f "$CV_SRC/martin_paul_eve.html" ]; then
    echo "==> Refreshing CV from $CV_SRC"
    cp "$CV_SRC/martin_paul_eve.pdf" c-v/Eve-CV.pdf
    cp "$CV_SRC/martin_paul_eve.html" _includes/publications.html
else
    echo "WARNING: $CV_SRC/martin_paul_eve.{pdf,html} not found; keeping existing CV files." >&2
fi

# --- 6. build the site as usual. This comes later because we need the atProto links in the source ---
echo "==> Building site"
# Plain jekyll, not `bundle exec`: the Nix jekyll (full variant) carries its
# own bundle incl. jekyll-feed; bundler would demand a local gem install.
jekyll build --incremental

# --- 7. commit (including .sequoia-state.json) + push ---
echo "==> Committing and pushing"
git add -A
if git diff --cached --quiet; then
    echo "Nothing new to commit — working tree clean."
else
    git commit -m "$MSG"
    git push
fi

echo "==> Pulling on server."

rsync -avz /home/martin/Documents/Programming/blog/_site/ evegd@reclaim:/home/evegd/blog/_site/

echo "==> Done."
