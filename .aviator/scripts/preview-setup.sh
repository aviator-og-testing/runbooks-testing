#!/usr/bin/env bash
#
# Aviator verify preview setup. Aviator runs this in the preview sandbox after
# checking out the branch. Its contract: start the services in the background
# and exit 0 once the website answers. It must NOT block, the services keep
# running in the sandbox after this script returns.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

# Backend (FastAPI) on :8000, seeded with the demo users and posts.
(
  cd backend_python
  uv sync
  nohup env RUNBOOKS_TESTING_SEED_DEMO=1 RUNBOOKS_TESTING_DB_PATH=/tmp/runbooks_testing.db \
    uv run uvicorn runbooks_testing_api.main:app --host 0.0.0.0 --port 8000 \
    > /tmp/backend.log 2>&1 &
)

# Frontend (node) on :3000, proxying /api to the backend.
(
  cd frontend
  npm install
  nohup env PORT=3000 API_TARGET=http://localhost:8000 node server.js \
    > /tmp/frontend.log 2>&1 &
)

# Wait for the website to answer before declaring the preview ready.
for _ in $(seq 1 60); do
  if curl -sf http://localhost:3000 > /dev/null; then
    echo "preview is up on :3000"
    exit 0
  fi
  sleep 2
done

echo "preview did not come up in time" >&2
cat /tmp/backend.log /tmp/frontend.log >&2 || true
exit 1
