# MedGuard Mock Frontend

Static test UI for checking the backend features. This is not the real frontend; it is only a working mock so teammates can exercise the API.

## Run

Start the backend first:

```powershell
cd "C:\Users\johnn\OneDrive\Documents\New project\backend"
docker compose up -d
uvicorn app.main:app --reload
```

Then start this mock frontend:

```powershell
cd "C:\Users\johnn\OneDrive\Documents\New project\mock-frontend"
python -m http.server 3000
```

Open:

```text
http://127.0.0.1:3000
```

## What It Tests

- Register and login
- Profile loading
- Dashboard stats
- Medication creation
- Reminder creation
- Dose logging
- Safety-check creation
- Doctor report creation
- Caregiver sharing

