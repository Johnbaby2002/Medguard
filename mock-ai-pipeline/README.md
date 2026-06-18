# MedGuard Safety Pipeline Trigger

This helper logs in and triggers the backend's rule-based safety engine. The interaction analysis itself is implemented in the FastAPI backend.

It is intended only for integration testing and demonstrations.

## Run Once

Start and seed the backend first. Then, from the repository root:

```powershell
cd mock-ai-pipeline
pip install -r requirements.txt
python mock_ai_pipeline.py --email patient@example.com --password StrongPassword123
```

## Run Continuously

```powershell
python mock_ai_pipeline.py --email patient@example.com --password StrongPassword123 --poll
```

## Use Another Backend URL

```powershell
python mock_ai_pipeline.py --base-url http://127.0.0.1:8001/api/v1 --email patient@example.com --password StrongPassword123
```

Safety results are informational and are not medical advice.
