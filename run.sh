#!/usr/bin/env bash
set -euo pipefail

echo "== QR Business Card: fast local run =="

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

"$SCRIPT_DIR/scripts/preflight.sh"

# Source backend env so child processes inherit (DATABASE_URL, ENV, etc.)
if [ -f "$SCRIPT_DIR/backend/.env" ]; then
  echo "[run] Sourcing backend/.env"
  set -a
  # shellcheck disable=SC1090
  source "$SCRIPT_DIR/backend/.env"
  set +a
fi

"$SCRIPT_DIR/scripts/run_db.sh"

echo "[run] Launching backend..."
(
  bash "$SCRIPT_DIR/scripts/run_backend.sh"
) &
BACKEND_PID=$!

sleep 2
echo "[run] Backend pid: $BACKEND_PID"

# Wait for backend health
for i in {1..30}; do
  if curl -sSf http://localhost:3001/healthz >/dev/null 2>&1; then
    echo "[run] Backend is healthy at http://localhost:3001/healthz"
    break
  fi
  sleep 0.5
done

mkdir -p "$SCRIPT_DIR/.pids"
echo "$BACKEND_PID" > "$SCRIPT_DIR/.pids/backend.pid"

echo "[run] Services starting."
echo "[run] Backend health: http://localhost:3001/healthz"
echo "[run] To stop cleanly: ./scripts/stop.sh"

# Optional: run automated local test
if [ "${RUN_TEST:-}" = "1" ]; then
  echo "[run] RUN_TEST=1 set — running scripts/test_local.sh"
  bash "$SCRIPT_DIR/scripts/test_local.sh" || true
fi

wait
