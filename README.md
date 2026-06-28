# MedGuard

MedGuard is a medication safety support project. The backend provides authentication, health profiles, medication, supplement, and substance/lifestyle CRUD, rule-based interaction checks, reminders, caregiver access, organization-ready roles, and doctor-ready JSON reports.

The system is medically cautious. It does not diagnose disease and does not replace doctors or pharmacists. Safety responses include:

```text
This is not medical advice. Consult a doctor or pharmacist.
```

## Quick Start

Use these commands from the project root:

```bash
cd Medguard
npm install
npm run setup
npm run dev
```

Open:

```text
Frontend: http://127.0.0.1:3000/register.html
Backend docs: http://127.0.0.1:8000/docs
```

Useful commands:

```bash
npm run backend    # backend only
npm run frontend   # frontend pages only
npm run test       # backend tests
```

Requirements:

- Node.js 18+
- Python 3.11+

`npm run setup` creates `backend/.venv`, installs Python dependencies, and creates a local SQLite `.env` file. No Docker or PostgreSQL is required for the quick prototype run.

## Key Features

- Medication management with manual entry, camera capture, upload, and barcode/OCR starter endpoints
- Substances and lifestyle tracking for alcohol, caffeine, nicotine, birth control, grapefruit, OTC medicines, and non-judgmental placeholders
- AI-powered medication safety check integration point
- Drug-drug, drug-food, and drug-supplement interaction detection
- Smart medication reminders and missed-dose tracking
- Personalized health profile for more accurate risk assessment
- Personalized medication risk score
- Plain-language explanations of interaction risks
- Doctor-ready medication reports
- Caregiver access and shared medication management
- Medication history and adherence tracking
- Emergency medication card for urgent-care handoff
- Risk dashboard, medication timeline, refill reminders, side effect tracker, rule-based assistant, and temporary doctor sharing links

## Future Roadmap

- OCR prescription scanning
- Wearable and EHR integration
- Predictive AI for high-risk patients
- Multi-language support
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
scripts/
  setup.mjs
  dev.mjs
ai-starter/
  API_CONTRACT.md
  client_example.py
ai-pipeline/
  medguard_ai_pipeline.py
```

## Database Options

SQLite is the easiest local option and is used by `npm run setup`.

PostgreSQL is available for a more production-like setup.

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
http://127.0.0.1:3000/register.html
```

These pages are a handoff starter for the frontend team. Registration and login are separate pages: start at `register.html`, then the app opens `login.html` after account creation. The pages show expected screens, fields, and endpoint mappings without locking the team into a framework.

## Main API Endpoints

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`
- `GET /auth/me`
- `GET /dashboard/summary`
- `GET /dashboard/risk-summary`
- `GET /profile`
- `PUT /profile`
- `POST /medications`
- `GET /medications`
- `GET /medications/{id}`
- `PUT /medications/{id}`
- `DELETE /medications/{id}`
- `GET /medications/history`
- `POST /scans/barcode`
- `POST /scans/camera`
- `POST /scans/upload`
- `POST /scans/prescription-ocr`
- `GET /scans`
- `POST /supplements`
- `GET /supplements`
- `GET /supplements/{id}`
- `PUT /supplements/{id}`
- `DELETE /supplements/{id}`
- `POST /substances`
- `GET /substances`
- `PUT /substances/{id}`
- `DELETE /substances/{id}`
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
- `GET /timeline/today`
- `GET /adherence/summary`
- `GET /refills/due`
- `POST /side-effects`
- `GET /side-effects`
- `GET /side-effects/summary`
- `POST /assistant/ask`
- `GET /assistant/status`
- `POST /share/report-link`
- `GET /share/report/{token}`
- `GET /reports/medication-summary`
- `GET /emergency-card`
- `POST /caregiver/invite`
- `GET /caregiver/patients`
- `GET /caregiver/patients/{id}/medications`
- `GET /caregiver/patients/{id}/reminders`
- `GET /caregiver/patients/{id}/missed-doses`
- `GET /caregiver/patients/{id}/report`
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

## Prototype Limitations

- The assistant can call the local `ai-pipeline/medguard_ai_pipeline.py` starter through `AI_PIPELINE_PATH` and `AI_PIPELINE_MODULE`. This is still rule-based until the AI team replaces it with a real model.
- Interaction rules are seed examples for an MVP and are not a complete clinical database.
- The share link is a temporary read-only report prototype.
- Timeline and adherence use local server time for MVP scheduling.
- MedGuard does not diagnose, prescribe, or replace medical advice from a doctor or pharmacist.

## Team Notes

- Backend owns user data, CRUD, safety rule checks, reminders, reports, and access control.
- AI pipeline should call backend APIs instead of writing directly to the database.
- Frontend should use the OpenAPI docs at `/docs` and the contract at `backend/docs/frontend-api-contract.md`.
- Never commit `.env`, database files, virtual environments, API keys, or generated build folders.
