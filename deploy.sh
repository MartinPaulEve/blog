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
#   ./deploy.sh --local ...    # ignore REMOTE_BUILD_HOST, run it all here
#   ./deploy.sh --remote-check # verify every hop a remote build needs
#   ./deploy.sh --no-cache-sync ...   # skip the server cache pull/push
#
# With REMOTE_BUILD_HOST=<ssh host> in .env (REMOTE_BUILD_DIR names its
# checkout; default ~/build/martineve/blog), only the local preparation —
# cover resize, CV refresh, commit and push — runs here; the host then
# pulls the branch and runs the rest (Sequoia, feeds, build, deposits,
# rsync, webmentions, BIROn) through its own copy of this script, so
# inside the same container image, with this machine's SSH agent
# forwarded for signing and for reaching the deploy server. For when the
# connection here is too thin to rsync the site. The deploy server also
# holds the canonical PDF/OG build cache, pulled before every build, so
# unchanged pages never re-render or re-ship whichever machine builds.
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
