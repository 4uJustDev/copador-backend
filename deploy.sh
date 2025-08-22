#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$HOME/tt-oak-company-backend"
LOG_FILE="$APP_DIR/deploy.log"

# логирование
exec > >(tee -a "$LOG_FILE") 2>&1

echo "[deploy] started at $(date)"

cd "$APP_DIR"

echo "[deploy] fetch/reset to origin/master…"
git fetch --all
git reset --hard origin/master

echo "[deploy] docker compose up -d --build…"
docker compose pull || true
docker compose up -d --build

echo "[deploy] cleaning old docker images…"
docker image prune -af || true

echo "[deploy] health check…"
for i in {1..30}; do
  if curl -sf http://127.0.0.1:8101/health >/dev/null; then
    echo "[deploy] API is healthy."
    echo "[deploy] finished at $(date)"
    exit 0
  fi
  sleep 2
done

echo "[deploy] health failed — last logs:"
docker compose logs --no-color api | tail -n 200
exit 1
