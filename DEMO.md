# MedGuard Demo Guide

Run all commands from the repository root unless a section says otherwise.

## 1. Start the Backend

The easiest option uses SQLite and does not require Docker:

```powershell
cd backend
.\start-local-sqlite.ps1
```

Keep this terminal running. The script prints the API and Swagger documentation URLs.

For PostgreSQL through Docker Desktop:

```powershell
cd backend
.\start-postgres-docker.ps1
```

If the default port is occupied, the start script automatically selects the next available port.

Useful backend helpers:

```powershell
.\show-medguard-ports.ps1
.\stop-medguard-backends.ps1
```

Return to the repository root before continuing:

```powershell
cd ..
```

## 2. Seed Demo Data

Open a second terminal in the repository root:

```powershell
cd demo-seed
pip install -r requirements.txt
python seed_demo.py
```

The script creates generic demonstration accounts:

```text
patient@example.com / StrongPassword123
caregiver@example.com / StrongPassword123
```

If the backend selected a port other than `8000`, set the API URL first:

```powershell
$env:MEDGUARD_API_BASE_URL="http://127.0.0.1:8001/api/v1"
python seed_demo.py
```

## 3. Trigger the Safety Engine

Open another terminal in the repository root:

```powershell
cd mock-ai-pipeline
pip install -r requirements.txt
python mock_ai_pipeline.py --email patient@example.com --password StrongPassword123
```

To run repeatedly:

```powershell
python mock_ai_pipeline.py --email patient@example.com --password StrongPassword123 --poll
```

## 4. Start the Mock Frontend

Open another terminal in the repository root:

```powershell
cd mock-frontend
python -m http.server 3000
```

Open:

```text
http://127.0.0.1:3000
```

Log in with the generic patient account and test medications, supplements, reminders, safety checks, reports, and caregiver access.
