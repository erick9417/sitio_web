#!/usr/bin/env bash
# Deploy helper script
# Usage: pull_and_restart.sh
# The script expects the repository to already be checked out on the server.

set -euo pipefail

REPO_DIR="$(dirname "$(realpath "$0")")/.."
# try to read optional env vars
BRANCH=${DEPLOY_BRANCH:-main}
SERVICE=${DEPLOY_SERVICE:-api.service}

echo "[deploy] starting deploy: branch=${BRANCH} repo_dir=${REPO_DIR}"

cd "$REPO_DIR"

if [ -d .git ]; then
  echo "[deploy] fetching latest from origin/${BRANCH}"
  git fetch --all --prune
  git reset --hard "origin/${BRANCH}"
else
  echo "[deploy] no .git found in $REPO_DIR, skipping git pull"
fi

# Optionally install/update Python deps
if [ -f requirements.txt ]; then
  echo "[deploy] installing Python requirements (pip)"
  python3 -m pip install -r requirements.txt --upgrade
fi

echo "[deploy] restarting service: ${SERVICE}"
if command -v systemctl >/dev/null 2>&1; then
  sudo systemctl restart "${SERVICE}" || echo "[deploy] warning: systemctl restart failed"
else
  echo "[deploy] systemctl not found — you may need to restart services manually"
fi

echo "[deploy] done"
