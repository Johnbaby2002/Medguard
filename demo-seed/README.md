# MedGuard Demo Seed

This helper creates generic users and sample data for testing the backend, mock frontend, and safety engine.

## Run

Start the backend first. Then, from the repository root:

```powershell
cd demo-seed
pip install -r requirements.txt
python seed_demo.py
```

It creates:

- `patient@example.com` / `StrongPassword123`
- `caregiver@example.com` / `StrongPassword123`
- Two medications
- One supplement
- One reminder and taken-dose log
- One safety-check result
- One caregiver permission

These credentials are for local demonstration only.
