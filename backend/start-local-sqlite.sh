#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.sqlite.example .env
  echo "Created .env using local SQLite settings."
fi

python dev.py
