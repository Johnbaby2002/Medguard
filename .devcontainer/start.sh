#!/usr/bin/env bash

set -u

ROOT="/workspaces/Medguard"

pkill -f "python dev.py" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true

cd "$ROOT/backend"

if [ ! -f ".env" ]; then
  cp .env.sqlite.example .env
fi

export DATABASE_URL="sqlite:///./medguard_v2.db"
export CORS_ORIGINS='["http://localhost:5173","http://127.0.0.1:5173"]'

nohup bash -lc '
  cd /workspaces/Medguard/backend
  exec python dev.py
' > "$ROOT/backend/backend.log" 2>&1 </dev/null &

cd "$ROOT/frontend"

nohup bash -lc '
  cd /workspaces/Medguard/frontend
  exec npm run dev -- --host 0.0.0.0 --port 5173
' > "$ROOT/frontend/frontend.log" 2>&1 </dev/null &

sleep 5

echo "=== Listening ports ==="
ss -ltnp | grep -E '8000|5173' || true

echo "=== Backend log ==="
tail -n 30 "$ROOT/backend/backend.log" || true

echo "=== Frontend log ==="
tail -n 30 "$ROOT/frontend/frontend.log" || true