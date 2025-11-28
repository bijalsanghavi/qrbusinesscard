#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."/backend

if [ ! -f .env ]; then
  echo "backend/.env missing; create it first" >&2
  exit 1
fi

set -a; source .env; set +a

python3 -m app.cli create-db

