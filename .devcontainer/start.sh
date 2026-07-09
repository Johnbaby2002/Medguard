#!/bin/bash

pkill -f uvicorn || true
pkill -f vite || true

cd backend

nohup uvicorn app.main:create_app \
  --factory \
  --host 0.0.0.0 \
  --port 8000 \
  > backend.log 2>&1 &

cd ../frontend

nohup npm run dev -- --host 0.0.0.0 \
  > frontend.log 2>&1 &