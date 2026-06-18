$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

if (-not (Test-Path -LiteralPath ".venv")) {
  python -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

if (-not (Test-Path -LiteralPath ".env")) {
  Copy-Item -LiteralPath ".env.example" -Destination ".env"
  Write-Host "Created .env using PostgreSQL Docker settings."
}

docker compose up -d

Write-Host ""
function Test-PortInUse {
  param([int]$Port)
  $connection = Get-NetTCPConnection -LocalAddress 127.0.0.1 -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
  return $null -ne $connection
}

$port = if ($env:PORT) { [int]$env:PORT } else { 8000 }
while (Test-PortInUse -Port $port) {
  Write-Host "Port $port is already in use. Trying $($port + 1)..."
  $port += 1
}

Write-Host "Starting MedGuard backend on http://127.0.0.1:$port"
Write-Host "Swagger docs: http://127.0.0.1:$port/docs"
Write-Host ""

& ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port $port
