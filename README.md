# MedGuard

MedGuard is a medication safety support project. The backend provides authentication, health profiles, medication and supplement CRUD, rule-based interaction checks, reminders, caregiver access, organization-ready roles, and doctor-ready JSON reports.

The system is medically cautious. It does not diagnose disease and does not replace doctors or pharmacists. Safety responses include:

```text
This is not medical advice. Consult a doctor or pharmacist.
```

## Key Features

- Medication management with manual entry and future barcode scanning support
- AI-powered medication safety check integration point
- Drug-drug, drug-food, and drug-supplement interaction detection
- Smart medication reminders and missed-dose tracking
- Personalized health profile for more accurate risk assessment
- Personalized medication risk score
- Plain-language explanations of interaction risks
- Doctor-ready medication reports
- Caregiver access and shared medication management
- Medication history and adherence tracking

## Future Roadmap

- OCR prescription scanning
- Wearable and EHR integration
- Predictive AI for high-risk patients
- Multi-language support
- Emergency medication card
- Pharmacy and insurance integration for B2B use cases

## Repository Structure

```text
backend/
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
  migrations/
  tests/
  docker-compose.yml
  dev.py
frontend-pages/
  *.html
  api-map.json
ai-starter/
  API_CONTRACT.md
  client_example.py
```

## Backend Database

PostgreSQL is the main database.

The local Docker database uses:

```text
postgresql+psycopg://medguard:medguard@localhost:5432/medguard
```

SQLite is still available for quick local testing through `backend/.env.sqlite.example`.

## Run Backend On Windows

```powershell
cd backend
.\start-postgres-docker.ps1
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Run Backend On macOS Or Linux

```bash
cd backend
chmod +x start-postgres-docker.sh
./start-postgres-docker.sh
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Run Without Docker

Windows:

```powershell
cd backend
.\start-local-sqlite.ps1
```

macOS/Linux:

```bash
cd backend
chmod +x start-local-sqlite.sh
./start-local-sqlite.sh
```

## Run Frontend Handoff Pages

```bash
cd frontend-pages
python -m http.server 3000
```

Open:

```text
http://127.0.0.1:3000
```

These pages are a handoff starter for the frontend team. They show the expected screens, fields, and endpoint mappings without locking the team into a framework.

## Main API Endpoints

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `GET /profile`
- `PUT /profile`
- `POST /medications`
- `GET /medications`
- `GET /medications/{id}`
- `PUT /medications/{id}`
- `DELETE /medications/{id}`
- `GET /medications/history`
- `POST /scans/barcode`
- `POST /scans/prescription-ocr`
- `GET /scans`
- `POST /supplements`
- `GET /supplements`
- `GET /supplements/{id}`
- `PUT /supplements/{id}`
- `DELETE /supplements/{id}`
- `POST /safety-check`
- `GET /interactions/history`
- `POST /ai/safety-checks`
- `GET /ai/safety-checks/pending`
- `GET /ai/safety-checks/{id}`
- `PUT /ai/safety-checks/{id}/result`
- `POST /reminders`
- `GET /reminders/today`
- `PUT /reminders/{id}`
- `DELETE /reminders/{id}`
- `POST /reminders/{id}/taken`
- `POST /reminders/{id}/missed`
- `GET /reports/medication-summary`
- `GET /emergency-card`
- `POST /caregiver/invite`
- `GET /caregiver/patients`
- `GET /caregiver/patients/{id}/medications`
- `POST /integrations`
- `GET /integrations`
- `GET /localization/languages`

All endpoints are also available under `/api/v1`.

## Tests

```bash
cd backend
python -m pip install -r requirements-dev.txt
python -m pytest
```

## Team Notes

- Backend owns user data, CRUD, safety rule checks, reminders, reports, and access control.
- AI pipeline should call backend APIs instead of writing directly to the database.
- Frontend should use the OpenAPI docs at `/docs` and the contract at `backend/docs/frontend-api-contract.md`.
- Never commit `.env`, database files, virtual environments, API keys, or generated build folders.
