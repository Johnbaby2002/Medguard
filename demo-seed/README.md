# MedGuard Demo Seed

Small helper to create demo users and data for testing the backend, mock frontend, and mock AI pipeline.

## Run

Start backend first, then:

```powershell
cd "C:\Users\johnn\OneDrive\Documents\New project\demo-seed"
python seed_demo.py
```

It creates:

- `patient@example.com` / `StrongPassword123`
- `caregiver@example.com` / `StrongPassword123`
- Two medications
- One reminder
- One dose log
- One pending safety check

