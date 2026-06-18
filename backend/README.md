# MedGuard Backend

FastAPI backend for MedGuard. It supports authentication, health profiles, medication and supplement management, a rule-based medication safety engine, reminders, caregiver support, organization-ready access control, audit logging, and doctor-ready JSON reports.

The system is medically cautious: it does not diagnose disease and does not replace doctors. Safety results include: `This is not medical advice. Consult a doctor or pharmacist.`

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL via `psycopg`
- SQLite for easy local demos
- JWT authentication
- Alembic migration scaffold
- Pytest test suite

## Easiest Local Setup

No Docker needed:

```powershell
cd backend
.\start-local-sqlite.ps1
```

Open the printed docs URL, usually:

```text
http://127.0.0.1:8000/docs
```

If port `8000` is busy, the script automatically tries the next free port.

## PostgreSQL With Docker

Use this when Docker Desktop is running:

```powershell
cd backend
.\start-postgres-docker.ps1
```

## Useful Helpers

```powershell
.\show-medguard-ports.ps1
.\stop-medguard-backends.ps1
```

## Project Structure

```text
app/
  main.py
  config.py
  database.py
  models/
  schemas/
  routers/
  services/
  auth/
  rule_engine/
```

## Key Endpoints

Auth:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

Profile:

- `GET /profile`
- `PUT /profile`

Medications:

- `POST /medications`
- `GET /medications`
- `GET /medications/{id}`
- `PUT /medications/{id}`
- `DELETE /medications/{id}`

Supplements:

- `POST /supplements`
- `GET /supplements`
- `PUT /supplements/{id}`
- `DELETE /supplements/{id}`

Safety:

- `POST /safety-check`
- `GET /interactions/history`

Reminders:

- `POST /reminders`
- `GET /reminders/today`
- `PUT /reminders/{id}`
- `DELETE /reminders/{id}`
- `POST /reminders/{id}/taken`
- `POST /reminders/{id}/missed`

Reports:

- `GET /reports/medication-summary`

Caregiver:

- `POST /caregiver/invite`
- `GET /caregiver/patients`
- `GET /caregiver/patients/{id}/medications`

Organizations:

- `POST /organizations`
- `GET /organizations`
- `POST /organizations/{id}/members`

All routes are also available under `/api/v1`, for example `/api/v1/auth/login`.

## Rule Engine

Seeded rules cover:

- blood thinner + NSAID/painkiller
- sleeping pill + alcohol
- anxiety medication + sleeping pill
- medication + grapefruit
- duplicate NSAIDs
- antibiotic + birth control
- pre-workout/high caffeine + anxiety medication
- duplicate cold medicine ingredients

## Demo Flow

In terminal 1:

```powershell
cd backend
.\start-local-sqlite.ps1
```

In terminal 2:

```powershell
cd demo-seed
python seed_demo.py
```

In terminal 3:

```powershell
cd mock-ai-pipeline
python mock_ai_pipeline.py --email patient@example.com --password StrongPassword123
```

In terminal 4:

```powershell
cd mock-frontend
python -m http.server 3000
```

Open:

```text
http://127.0.0.1:3000
```

Demo login:

```text
patient@example.com
StrongPassword123
```

## Tests

```powershell
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest
```

## Alembic

Create and apply migrations:

```powershell
cd backend
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe change"
.\.venv\Scripts\python.exe -m alembic upgrade head
```
