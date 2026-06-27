# AI API Contract

Use JWT authentication:

```text
Authorization: Bearer <access_token>
```

## Create Review

`POST /ai/safety-checks`

```json
{
  "request_source": "ai-service"
}
```

Response contains:

- `id`
- `status`
- `input_snapshot`
- `disclaimer`

The `input_snapshot` includes profile fields, medications, supplements, and the backend rule-based safety result.

## Submit AI Result

`PUT /ai/safety-checks/{id}/result`

```json
{
  "status": "completed",
  "aiResult": {
    "summary": "Plain-language summary.",
    "riskScoreAdjustment": 0,
    "warnings": [],
    "recommendedActions": [],
    "disclaimer": "This is not medical advice. Consult a doctor or pharmacist."
  }
}
```

If the AI service fails:

```json
{
  "status": "failed",
  "errorMessage": "Reason the AI check could not be completed."
}
```

## Barcode And OCR Intake

The AI service can create medication drafts from scan data:

- `POST /scans/barcode`
- `POST /scans/prescription-ocr`

The backend stores drafts for review. A user or frontend should confirm the draft before saving it as a medication.
