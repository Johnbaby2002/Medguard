# MedGuard Backend

FastAPI backend for MedGuard. It supports JWT authentication, password hashing, user health profiles, medication CRUD, supplement CRUD, a rule-based interaction engine, reminders, caregiver access, organization-ready roles, audit logging, and doctor-ready JSON reports.

MedGuard is a medication safety support tool. It does not diagnose disease or replace clinicians. Safety results include:

```text
This is not medical advice. Consult a doctor or pharmacist.
```

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL with `psycopg`
- Alembic migration scaffold
- JWT authentication
- Pytest
- Optional SQLite for local tests/demo runs

## Environment

Copy the PostgreSQL example:

```bash
cp .env.example .env
```

Important values:

```text
DATABASE_URL=postgresql+psycopg://medguard:medguard@localhost:5432/medguard
JWT_SECRET_KEY=change-this-in-production
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

For a quick SQLite run, copy `.env.sqlite.example` instead.

## Windows Setup

```powershell
cd backend
.\start-postgres-docker.ps1
```

## macOS/Linux Setup

```bash
cd backend
chmod +x start-postgres-docker.sh
./start-postgres-docker.sh
```

## Manual Setup

macOS/Linux:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
docker compose up -d
python dev.py
```

Windows:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
docker compose up -d
.\.venv\Scripts\python.exe dev.py
```

Open:

```text
http://127.0.0.1:8000/docs
```

If port `8000` is busy, `dev.py` automatically tries the next available port.

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

## CRUD Modules

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
- `GET /medications/history`

Scan intake:

- `POST /scans/barcode`
- `POST /scans/camera`
- `POST /scans/upload`
- `POST /scans/prescription-ocr`
- `GET /scans`
- `POST /scans/{id}/medication`

Supplements:

- `POST /supplements`
- `GET /supplements`
- `GET /supplements/{id}`
- `PUT /supplements/{id}`
- `DELETE /supplements/{id}`

Safety:

- `POST /safety-check`
- `GET /interactions/history`

AI handoff:

- `POST /ai/safety-checks`
- `GET /ai/safety-checks/pending`
- `GET /ai/safety-checks/{id}`
- `PUT /ai/safety-checks/{id}/result`

Reminders:

- `POST /reminders`
- `GET /reminders/today`
- `PUT /reminders/{id}`
- `DELETE /reminders/{id}`
- `POST /reminders/{id}/taken`
- `POST /reminders/{id}/missed`

Reports:

- `GET /reports/medication-summary`
- `GET /emergency-card`

Caregiver:

- `POST /caregiver/invite`
- `GET /caregiver/patients`
- `GET /caregiver/patients/{id}/medications`

Organizations:

- `POST /organizations`
- `GET /organizations`
- `POST /organizations/{id}/members`

Future integrations:

- `POST /integrations`
- `GET /integrations`
- `GET /localization/languages`

Routes are also available under `/api/v1`, for example `/api/v1/medications`.

## Frontend-Friendly Payloads

The backend accepts snake_case and common camelCase request fields. These both work:

```json
{
  "active_ingredient": "ibuprofen",
  "medication_category": "nsaid",
  "is_prescription": false
}
```

```json
{
  "activeIngredient": "ibuprofen",
  "medicationCategory": "nsaid",
  "isPrescription": false
}
```

Medication `form` values are case-normalized, so `Tablet`, `tablet`, and `TABLET` from a select control are accepted. If `activeIngredient` is empty when creating a medication, the backend stores the medication name as a safe placeholder.

## Tests

```bash
cd backend
python -m pip install -r requirements-dev.txt
python -m pytest
```

## Alembic

```bash
cd backend
python -m alembic revision --autogenerate -m "describe change"
python -m alembic upgrade head
```
