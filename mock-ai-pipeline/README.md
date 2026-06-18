# MedGuard Mock AI Pipeline

This is a fake/rule-based pipeline for testing backend integration. It does not perform real medical analysis.

The script logs in as a user, reads that user's pending safety checks, and writes mock results back to the backend.

## Run Once

```powershell
cd "C:\Users\johnn\OneDrive\Documents\New project\mock-ai-pipeline"
python mock_ai_pipeline.py --email patient@example.com --password StrongPassword123
```

## Poll Continuously

```powershell
python mock_ai_pipeline.py --email patient@example.com --password StrongPassword123 --poll
```

Optional backend URL:

```powershell
python mock_ai_pipeline.py --base-url http://127.0.0.1:8000/api/v1 --email patient@example.com --password StrongPassword123
```

## Mock Rules

The fake result flags a higher risk when medication names or ingredients contain examples such as:

- warfarin + ibuprofen
- sleeping pill + alcohol
- grapefruit
- duplicate active ingredients

Again, this is only for demo/testing.
