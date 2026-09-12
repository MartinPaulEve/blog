#!/usr/bin/env bash
#
# mailthought entrypoint: turn the environment contract into the state
# the pipeline expects — SSH identities and the `reclaim` alias that
# evedeploy's hardcoded rsync target resolves through, a git identity,
# the blog clone on the /data volume (first boot only), and the
# clone's .env that thought_composer/evedeploy read their tokens from
# — then hand over to gunicorn.
set -euo pipefail

DATA_DIR="${DATA_DIR:-/data}"
BLOG_DIR="$DATA_DIR/blog"
GIT_REPO_URL="${GIT_REPO_URL:-git@github.com:MartinPaulEve/blog.git}"

mkdir -p "$DATA_DIR"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$DATA_DIR/uv-cache}"

# --- SSH -------------------------------------------------------------
SSH_DIR="$HOME/.ssh"
mkdir -p "$SSH_DIR"
chmod 700 "$SSH_DIR"

if [ -n "${GIT_SSH_KEY:-}" ]; then
    printf '%s\n' "$GIT_SSH_KEY" > "$SSH_DIR/id_git"
    chmod 600 "$SSH_DIR/id_git"
else
    echo "WARNING: GIT_SSH_KEY not set; cloning and pushing will fail." >&2
fi

RSYNC_KEY_SOURCE="${RSYNC_SSH_KEY:-${GIT_SSH_KEY:-}}"
if [ -n "$RSYNC_KEY_SOURCE" ]; then
    printf '%s\n' "$RSYNC_KEY_SOURCE" > "$SSH_DIR/id_rsync"
    chmod 600 "$SSH_DIR/id_rsync"
fi

cat /etc/mailthought/github_known_hosts >> "$SSH_DIR/known_hosts"
RECLAIM_STRICTNESS="accept-new"
if [ -n "${KNOWN_HOSTS:-}" ]; then
    printf '%s\n' "$KNOWN_HOSTS" >> "$SSH_DIR/known_hosts"
    RECLAIM_STRICTNESS="yes"
fi
sort -u "$SSH_DIR/known_hosts" -o "$SSH_DIR/known_hosts"
chmod 600 "$SSH_DIR/known_hosts"

{
    echo "Host github.com"
    echo "    IdentityFile $SSH_DIR/id_git"
    echo "    IdentitiesOnly yes"
    echo "    StrictHostKeyChecking yes"
    if [ -n "${RSYNC_HOST:-}" ]; then
        # evedeploy rsyncs to the host alias "reclaim"; resolve it here.
        echo "Host reclaim"
        echo "    HostName $RSYNC_HOST"
        echo "    User ${RSYNC_USER:-evegd}"
        echo "    Port ${RSYNC_PORT:-22}"
        echo "    IdentityFile $SSH_DIR/id_rsync"
        echo "    IdentitiesOnly yes"
        echo "    StrictHostKeyChecking $RECLAIM_STRICTNESS"
    fi
} > "$SSH_DIR/config"
chmod 600 "$SSH_DIR/config"
if [ -z "${RSYNC_HOST:-}" ]; then
    echo "WARNING: RSYNC_HOST not set; deploys will fail (thoughts still store and syndicate)." >&2
fi

# --- git -------------------------------------------------------------
git config --global user.name "${GIT_USER_NAME:-Martin Paul Eve}"
git config --global user.email "${GIT_USER_EMAIL:-martin@eve.gd}"
# The container is single-purpose and single-user; volume mounts can
# surface with a foreign uid (Coolify-managed volumes do), so trust
# every path rather than fail the clone on "dubious ownership".
git config --global --add safe.directory '*'

if [ ! -d "$BLOG_DIR/.git" ]; then
    echo "==> First boot: cloning $GIT_REPO_URL to $BLOG_DIR"
    git clone "$GIT_REPO_URL" "$BLOG_DIR"
fi

# --- the clone's .env (read by thought_composer and evedeploy) --------
{
    echo "BLUESKY_APP_PASSWORD=${BLUESKY_APP_PASSWORD:-}"
    [ -n "${BLUESKY_IDENTIFIER:-}" ] && echo "BLUESKY_IDENTIFIER=$BLUESKY_IDENTIFIER"
    echo "MASTODON_ACCESS_TOKEN=${MASTODON_ACCESS_TOKEN:-}"
    [ -n "${MASTODON_BASE_URL:-}" ] && echo "MASTODON_BASE_URL=$MASTODON_BASE_URL"
    true
} > "$BLOG_DIR/.env"
chmod 600 "$BLOG_DIR/.env"

# --- serve -----------------------------------------------------------
# One worker process: create_app starts the single pipeline thread, and
# builds/git must never run concurrently.
exec uv run --project /app gunicorn \
    --workers 1 --threads 8 --timeout 120 \
    --bind 0.0.0.0:8080 \
    "mailthought.app:create_app()"
