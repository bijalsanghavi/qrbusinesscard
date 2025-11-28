#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR/backend"

export ENV=${ENV:-development}
export FRONTEND_ORIGIN=${FRONTEND_ORIGIN:-http://localhost:3000}

if [ ! -f ".env" ]; then
  cp .env.example .env
fi

if [ ! -d ".venv" ]; then
  echo "[run_backend] Creating venv..."
  python3 -m venv .venv
fi

echo "[run_backend] Installing deps (if needed)..."
".venv/bin/pip" -q install -r requirements.txt

echo "[run_backend] Loading env vars from .env"
set -a
source .env
set +a

# Normalize DATABASE_URL to Docker port 5555 if needed
DBURL=${DATABASE_URL:-}
if [[ -z "$DBURL" ]]; then
  DBURL="postgresql+psycopg://postgres:postgres@localhost:5555/qrcard"
elif [[ "$DBURL" == *"@localhost:5432/"* ]]; then
  DBURL=${DBURL//@localhost:5432\//@localhost:5555/}
elif [[ "$DBURL" == *"@127.0.0.1:5432/"* ]]; then
  DBURL=${DBURL//@127.0.0.1:5432\//@127.0.0.1:5555/}
fi
export DATABASE_URL="$DBURL"
echo "[run_backend] Using DATABASE_URL=$DATABASE_URL"

# Normalize FRONTEND_ORIGIN to 3002 for local dev
F_ORIGIN=${FRONTEND_ORIGIN:-http://localhost:3002}
if [[ "$F_ORIGIN" == *":3000" ]]; then
  F_ORIGIN=${F_ORIGIN//:3000/:3002}
fi
export FRONTEND_ORIGIN="$F_ORIGIN"
echo "[run_backend] Using FRONTEND_ORIGIN=$FRONTEND_ORIGIN"

echo "[run_backend] Starting FastAPI (ENV=$ENV) on :3001 ..."
exec \
  env ENV="$ENV" FRONTEND_ORIGIN="$FRONTEND_ORIGIN" DATABASE_URL="$DATABASE_URL" \
  ".venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 3001 --reload
