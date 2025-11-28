#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)

"$ROOT_DIR/scripts/stop.sh"

echo "[clean] Removing docker volumes (db)"
docker compose down -v || true

echo "[clean] Removing local media uploads"
rm -rf "$ROOT_DIR/backend/media" || true
mkdir -p "$ROOT_DIR/backend/media"

echo "[clean] Frontend removed; nothing to clean there."

echo "[clean] Done."
