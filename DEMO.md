# MedGuard Demo Guide

This project now has three testable parts:

- `backend`: real FastAPI + PostgreSQL backend
- `mock-frontend`: simple static UI for testing backend features
- `mock-ai-pipeline`: fake safety-check worker for demo purposes

## 1. Start Backend And Database

Easiest option, no Docker needed:

```powershell
cd "C:\Users\johnn\OneDrive\Documents\New project\backend"
.\start-local-sqlite.ps1
```

PostgreSQL Docker option:

```powershell
cd "C:\Users\johnn\OneDrive\Documents\New project\backend"
.\start-postgres-docker.ps1
```

Backend docs:

```text
http://127.0.0.1:8000/docs
```

If `8000` is busy, the start script automatically tries `8001`, `8002`, and so on. Use the URL printed by the script.

To see what is using the common backend ports:

```powershell
cd "C:\Users\johnn\OneDrive\Documents\New project\backend"
.\show-medguard-ports.ps1
```

To stop old MedGuard backend processes:

```powershell
.\stop-medguard-backends.ps1
```

## 2. Seed Demo Data

Open a second terminal while the backend is still running:

```powershell
cd "C:\Users\johnn\OneDrive\Documents\New project\demo-seed"
pip install -r requirements.txt
python seed_demo.py
```

Demo accounts:

```text
patient@example.com / StrongPassword123
caregiver@example.com / StrongPassword123
```

## 3. Run Mock AI Pipeline

Process pending safety checks once:

```powershell
cd "C:\Users\johnn\OneDrive\Documents\New project\mock-ai-pipeline"
pip install -r requirements.txt
python mock_ai_pipeline.py --email patient@example.com --password StrongPassword123
```

Or keep polling:

```powershell
python mock_ai_pipeline.py --email patient@example.com --password StrongPassword123 --poll
```

## 4. Run Mock Frontend

```powershell
cd "C:\Users\johnn\OneDrive\Documents\New project\mock-frontend"
python -m http.server 3000
```

Open:

```text
http://127.0.0.1:3000
```

Use the patient account above, then test medications, reminders, dose logs, safety checks, reports, and caregiver sharing.
