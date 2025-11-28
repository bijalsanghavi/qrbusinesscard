#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
if [ ! -f "$ROOT_DIR/backend/.env" ]; then
  echo "[run_db] Creating backend/.env from example..."
  cp "$ROOT_DIR/backend/.env.example" "$ROOT_DIR/backend/.env"
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "[run_db] ERROR: Docker not found. Please install/start Docker Desktop and re-run."
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "[run_db] ERROR: Docker daemon not running. Start Docker Desktop and re-run."
  exit 1
fi

echo "[run_db] Starting Postgres via docker compose..."
docker compose up -d db
echo "[run_db] Waiting for Postgres to become ready..."
set +e
for i in {1..20}; do
  docker exec "$(docker compose ps -q db)" pg_isready -U postgres >/dev/null 2>&1 && break
  sleep 1
done
set -e
echo "[run_db] Postgres is up (container: qrcard-db)."
