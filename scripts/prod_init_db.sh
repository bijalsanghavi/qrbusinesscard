#!/usr/bin/env bash
# Initialize production database (creates tables)
# Usage:
#   Local with .env: ./scripts/prod_init_db.sh
#   Railway: railway run python -m app.cli create-db

set -euo pipefail

cd "$(dirname "$0")/../backend"

# Use environment variables if already set (e.g., in Railway/Docker)
# Otherwise, load from .env
if [ -z "${DATABASE_URL:-}" ] && [ -f .env ]; then
  echo "[init-db] Loading backend/.env"
  set -a; source .env; set +a
fi

if [ -z "${DATABASE_URL:-}" ]; then
  echo "[init-db] ERROR: DATABASE_URL not set. Either set it as env var or create backend/.env" >&2
  exit 1
fi

echo "[init-db] Running database initialization..."
python3 -m app.cli create-db
echo "[init-db] Done. Tables created/verified."

