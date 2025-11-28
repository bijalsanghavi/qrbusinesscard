#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)

function kill_pidfile() {
  local file="$1"
  if [ -f "$file" ]; then
    local pid
    pid=$(cat "$file" 2>/dev/null || echo "")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
      echo "[stop] Killing PID $pid from $(basename "$file")"
      kill "$pid" 2>/dev/null || true
      sleep 1
      kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$file"
  fi
}

echo "[stop] Stopping app processes (using pidfiles if present)"
kill_pidfile "$ROOT_DIR/.pids/backend.pid"

echo "[stop] Fallback: pkill by pattern (safe if duplicates exist)"
pkill -f "uvicorn app.main:app" 2>/dev/null || true

echo "[stop] Docker compose down"
docker compose down || true

echo "[stop] Done."
