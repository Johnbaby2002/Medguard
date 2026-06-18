@echo off
setlocal

set "PROJECT_DIR=C:\Users\johnn\OneDrive\Documents\New project\n8n-self-hosted"
set "DOCKER_DESKTOP=C:\Program Files\Docker\Docker\Docker Desktop.exe"
set "N8N_URL=http://localhost:5678"

echo Starting n8n...

docker info >nul 2>nul
if errorlevel 1 (
    echo Docker is not ready. Starting Docker Desktop...
    if exist "%DOCKER_DESKTOP%" (
        start "" "%DOCKER_DESKTOP%"
    ) else (
        echo Could not find Docker Desktop at "%DOCKER_DESKTOP%".
        pause
        exit /b 1
    )

    echo Waiting for Docker to start...
    for /l %%i in (1,1,60) do (
        docker info >nul 2>nul
        if not errorlevel 1 goto docker_ready
        timeout /t 5 /nobreak >nul
    )

    echo Docker did not become ready in time. Open Docker Desktop and try again.
    pause
    exit /b 1
)

:docker_ready
cd /d "%PROJECT_DIR%"
docker compose up -d
if errorlevel 1 (
    echo Failed to start n8n.
    pause
    exit /b 1
)

echo Opening n8n...
start "" "%N8N_URL%"
endlocal
