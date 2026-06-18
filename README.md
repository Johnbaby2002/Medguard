# MedGuard

MedGuard is a medication-safety support platform built with FastAPI. It provides health profiles, medication and supplement tracking, rule-based interaction warnings, reminders, caregiver access, organization-ready roles, and doctor-ready reports.

MedGuard does not diagnose conditions or replace professional care. Safety results are informational and include a reminder to consult a doctor or pharmacist.

## Project Contents

- `backend/`: FastAPI application, database models, rule engine, tests, and migrations
- `mock-frontend/`: lightweight browser interface for testing the API
- `demo-seed/`: script that creates reusable demonstration data
- `mock-ai-pipeline/`: helper that triggers the backend safety engine
- `DEMO.md`: complete demonstration walkthrough

## Quick Start

Clone the repository and open PowerShell in its root directory.

Start the backend with SQLite:

```powershell
cd backend
.\start-local-sqlite.ps1
```

Open the URL printed by the script, usually:

```text
http://127.0.0.1:8000/docs
```

In another terminal, seed demonstration data:

```powershell
cd demo-seed
python seed_demo.py
```

For the complete workflow, see [DEMO.md](DEMO.md).

## Main Technologies

- FastAPI
- SQLAlchemy
- PostgreSQL or SQLite
- JWT authentication
- Alembic
- Pytest

## Medical Disclaimer

This project provides medication-safety support only. It is not medical advice and should not be used to diagnose conditions or replace a doctor or pharmacist.
