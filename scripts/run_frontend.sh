#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR/frontend"

if [ ! -f ".env.local" ]; then
  cp .env.example .env.local
fi

echo "[run_frontend] Installing deps (if needed)..."
npm install --silent

# Ensure backend URL env is correct for port 3001
export NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL:-http://localhost:3001}
# Overwrite .env.local to avoid stale values
printf "NEXT_PUBLIC_BACKEND_URL=%s\n" "$NEXT_PUBLIC_BACKEND_URL" > .env.local

# Avoid inherited PORT interfering with Next
unset PORT || true

echo "[run_frontend] Using NEXT_PUBLIC_BACKEND_URL=$NEXT_PUBLIC_BACKEND_URL"
echo "[run_frontend] Starting Next.js on :3002 ..."
exec npm run dev
