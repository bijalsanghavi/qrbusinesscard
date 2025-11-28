#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)

echo "[preflight] Checking Docker..."
if ! command -v docker >/dev/null 2>&1; then
  echo "[preflight] ERROR: Docker not installed. Install Docker Desktop and retry." >&2
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "[preflight] ERROR: Docker daemon not running. Start Docker Desktop and retry." >&2
  exit 1
fi

echo "[preflight] Ensuring backend/.env exists..."
if [ ! -f "$ROOT_DIR/backend/.env" ]; then
  cp "$ROOT_DIR/backend/.env.example" "$ROOT_DIR/backend/.env"
fi

echo "[preflight] Checking DATABASE_URL..."
if ! grep -q "^DATABASE_URL=" "$ROOT_DIR/backend/.env"; then
  echo "DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5555/qrcard" >> "$ROOT_DIR/backend/.env"
else
  # Normalize to Docker-mapped port 5555 if it's using localhost:5432
  if grep -q "DATABASE_URL=.*@localhost:5432/" "$ROOT_DIR/backend/.env"; then
    sed -i '' 's/@localhost:5432\//@localhost:5555\//g' "$ROOT_DIR/backend/.env"
  fi
  if grep -q "DATABASE_URL=.*@127.0.0.1:5432/" "$ROOT_DIR/backend/.env"; then
    sed -i '' 's/@127.0.0.1:5432\//@127.0.0.1:5555\//g' "$ROOT_DIR/backend/.env"
  fi
fi

echo "[preflight] Ensuring media directory exists..."
mkdir -p "$ROOT_DIR/backend/media"

echo "[preflight] Checking Node and Python..."
node -v >/dev/null 2>&1 || echo "[preflight] WARN: Node not found in PATH"
python3 -V >/dev/null 2>&1 || echo "[preflight] WARN: Python3 not found in PATH"

echo "[preflight] OK"

echo "[preflight] Config summary:"
echo "  - DATABASE_URL=$(grep '^DATABASE_URL=' "$ROOT_DIR/backend/.env" | sed 's/DATABASE_URL=//')"
echo "  - GOOGLE_CLIENT_ID set? $(grep -q '^GOOGLE_CLIENT_ID=' "$ROOT_DIR/backend/.env" && echo yes || echo no)"
echo "  - GOOGLE_CLIENT_SECRET set? $(grep -q '^GOOGLE_CLIENT_SECRET=' "$ROOT_DIR/backend/.env" && echo yes || echo no)"
echo "  - FRONTEND_ORIGIN=${FRONTEND_ORIGIN:-http://localhost:3002}"
echo "  - NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL:-http://localhost:3001}"
