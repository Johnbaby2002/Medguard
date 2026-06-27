$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

if (-not (Test-Path -LiteralPath ".venv")) {
  python -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

if (-not (Test-Path -LiteralPath ".env")) {
  Copy-Item -LiteralPath ".env.sqlite.example" -Destination ".env"
  Write-Host "Created .env using SQLite local settings."
}

$env:DATABASE_URL = "sqlite:///./medguard_v2.db"
$env:CORS_ORIGINS = '["http://localhost:3000","http://127.0.0.1:3000"]'

& ".\.venv\Scripts\python.exe" dev.py
