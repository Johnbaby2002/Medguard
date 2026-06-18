# MedGuard Mock Frontend

This lightweight static interface is provided for exercising the MedGuard API. It is a testing and demonstration client, not the production frontend.

## Run

Start the backend first:

```powershell
cd backend
.\start-local-sqlite.ps1
```

In another terminal, from the repository root:

```powershell
cd mock-frontend
python -m http.server 3000
```

Open:

```text
http://127.0.0.1:3000
```

If the backend selected a different port, update the API URL field at the top of the page.

## Features Covered

- Registration and login
- Dashboard summary
- Medication creation
- Reminder creation
- Dose status
- Safety checks
- Medication reports
- Caregiver access
