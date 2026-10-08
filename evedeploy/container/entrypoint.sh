#!/usr/bin/env bash
# Become the operator. Docker starts us as root with EVEDEPLOY_UID/GID and
# HOME describing the host user; create a matching account (ssh and git
# both need a passwd entry) and drop privileges. Under Podman with
# --userns=keep-id we already run as that user, so just exec.
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    exec "$@"
fi

uid="${EVEDEPLOY_UID:-1000}"
gid="${EVEDEPLOY_GID:-1000}"
home="${HOME:-/home/deploy}"

getent group "$gid" >/dev/null || groupadd -g "$gid" deploy
if ! getent passwd "$uid" >/dev/null; then
    useradd -u "$uid" -g "$gid" -d "$home" -M -s /bin/bash deploy
fi
user="$(getent passwd "$uid" | cut -d: -f1)"

# Bind mounts under $HOME (~/.ssh, ~/.config/git/config) leave their parent
# directories root-owned; hand the dot-directories Chromium, uv and git
# write into back to the operator (not recursive: the mounts stay as they
# are).
mkdir -p "$home/.config" "$home/.cache" "$home/.local/share" \
    "${UV_CACHE_DIR:-/var/cache/uv}"
chown "$uid:$gid" "$home" "$home/.config" "$home/.cache" "$home/.local" \
    "$home/.local/share" "${UV_CACHE_DIR:-/var/cache/uv}"

exec setpriv --reuid="$uid" --regid="$gid" --init-groups \
    env HOME="$home" USER="$user" LOGNAME="$user" "$@"
