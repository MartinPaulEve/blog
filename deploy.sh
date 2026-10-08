#!/usr/bin/env bash
#
# deploy.sh — runs the evedeploy pipeline (see evedeploy/) inside its
# container image, so the only host requirements are Docker or Podman, an
# SSH agent holding the deploy and signing keys, and python3. The image is
# built on first use (and rebuilt when its inputs change); the repository,
# ~/.ssh, the git config and the agent socket are passed through, so the
# terminal output, the confirmation gate and Ctrl+C behave exactly as
# before. All evedeploy arguments are forwarded:
#
#   ./deploy.sh ["commit message"]
#   ./deploy.sh --no-resize ["commit message"]
#   ./deploy.sh --no-sequoia ["commit message"]   # skip the ATProto publish
#   ./deploy.sh --build-only   # local build + preview server, no deploy
#   ./deploy.sh --build-only --no-server   # build only, no server
#   ./deploy.sh --quick        # jekyll build + rsync only (short thoughts)
#
# Launcher-only switches (consumed here, never passed on):
#
#   ./deploy.sh --native ...   # old behaviour: host toolchain, no container
#   ./deploy.sh --shell        # a bash prompt inside the container
#   ./deploy.sh --rebuild-image ...   # force a fresh image build first
#
# Environment: EVEDEPLOY_RUNTIME=docker|podman picks the runtime;
# EVEDEPLOY_SSH_AGENT=/path/to/agent.sock names the agent to sign with
# (default: Bitwarden's, then 1Password's, then $SSH_AUTH_SOCK).

cd "$(dirname "$0")"
exec python3 evedeploy/evedeploy/container.py "$@"
