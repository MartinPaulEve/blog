#!/usr/bin/env bash
#
# newdeploy.sh — compatibility shim. The deployment pipeline now lives in
# the evedeploy Python app (see evedeploy/); this forwards all arguments:
#
#   ./newdeploy.sh ["commit message"]
#   ./newdeploy.sh --no-resize ["commit message"]
#   ./newdeploy.sh --build-only   # local build to _site only, no deploy

cd "$(dirname "$0")"
exec uv run --project evedeploy evedeploy "$@"
