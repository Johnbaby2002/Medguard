#!/bin/bash

pkill -f uvicorn || true
pkill -f vite || true
pkill -f "python dev.py" || true

cd /workspaces/Medguard/backend

if [ ! -f ".env" ]; then
  cp .env.sqlite.example .env
fi

export DATABASE_URL="sqlite:///./medguard_v2.db"
export CORS_ORIGINS='["http://localhost:5173","http://127.0.0.1:5173"]'

nohup python dev.py \
  > backend.log 2>&1 &

cd /workspaces/Medguard/frontend

nohup npm run dev -- --host 0.0.0.0 \
  > frontend.log 2>&1 &