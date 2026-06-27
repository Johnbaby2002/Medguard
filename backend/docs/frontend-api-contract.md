# Frontend API Contract

Base URL:

```text
http://127.0.0.1:8000
```

The backend also exposes `/api/v1` aliases:

```text
http://127.0.0.1:8000/api/v1
```

Use:

```text
Authorization: Bearer <access_token>
```

Requests accept backend-style `snake_case` and common frontend-style `camelCase` field names.

## Auth

`POST /auth/register`

```json
{
  "email": "patient@example.com",
  "password": "StrongPassword123",
  "fullName": "Alex Patient",
  "role": "patient"
}
```

`POST /auth/login`

```json
{
  "email": "patient@example.com",
  "password": "StrongPassword123"
}
```

`GET /auth/me`

## Health Profile

`GET /profile`

`PUT /profile`

```json
{
  "age": 70,
  "sex": "male",
  "weight": 82,
  "knownConditions": ["atrial fibrillation"],
  "allergies": ["penicillin"],
  "pregnancyStatus": null,
  "alcoholUse": "occasional",
  "caffeinePreworkoutUse": "none"
}
```

## Medications

`POST /medications`

```json
{
  "name": "Warfarin",
  "activeIngredient": "warfarin",
  "dosage": "5mg",
  "form": "tablet",
  "frequency": "once daily",
  "startDate": "2026-06-16",
  "endDate": null,
  "prescribingDoctor": "Dr. Smith",
  "notes": "Take in the evening",
  "medicationCategory": "blood thinner",
  "isPrescription": true
}
```

`activeIngredient` may be left empty during early frontend work. The backend will store the medication name as a placeholder.

`GET /medications`

`GET /medications/{id}`

`PUT /medications/{id}`

`DELETE /medications/{id}`

`GET /medications/history`

Returns dose/adherence logs and summary:

```json
{
  "logs": [],
  "adherence_summary": {
    "total_logs": 0,
    "taken": 0,
    "missed": 0,
    "adherence_rate_percent": null
  }
}
```

## Scan Intake

`POST /scans/barcode`

```json
{
  "barcode": "0123456789012",
  "productName": "Ibuprofen",
  "activeIngredient": "ibuprofen",
  "dosage": "200mg",
  "notes": "Optional package notes"
}
```

`POST /scans/camera`

```json
{
  "imageData": "data:image/png;base64,...",
  "fileName": "camera-capture.png",
  "contentType": "image/png",
  "notes": "Optional user note"
}
```

`POST /scans/upload`

Send `multipart/form-data`:

```text
file=<image or PDF>
ocr_text=<optional OCR text>
notes=<optional user note>
```

`POST /scans/prescription-ocr`

```json
{
  "ocrText": "Amoxicillin\n500mg capsule",
  "imageReference": "optional-file-or-storage-reference"
}
```

`GET /scans`

`POST /scans/{id}/medication`

```json
{
  "name": "Optional override",
  "frequency": "once daily"
}
```

Scan endpoints return medication drafts for review. The frontend can save a reviewed draft as a real medication with `POST /scans/{id}/medication`.

## Supplements

`POST /supplements`

```json
{
  "name": "Pre-workout",
  "activeIngredientCategory": "caffeine",
  "dose": "1 scoop",
  "frequency": "before exercise",
  "notes": "High caffeine"
}
```

`GET /supplements`

`GET /supplements/{id}`

`PUT /supplements/{id}`

`DELETE /supplements/{id}`

## Safety

`POST /safety-check`

Returns:

```json
{
  "total_risk_score": 6,
  "interactions": [
    {
      "severity": "high",
      "interaction_type": "drug_drug",
      "explanation": "Combining a blood thinner with an NSAID or painkiller can increase bleeding risk.",
      "recommendation": "Ask a doctor or pharmacist before combining these medicines.",
      "disclaimer": "This is not medical advice. Consult a doctor or pharmacist.",
      "matched_items": ["Ibuprofen", "Warfarin"]
    }
  ],
  "highest_severity": "high",
  "recommended_actions": ["Ask a doctor or pharmacist before combining these medicines."],
  "safe_timing_suggestions": ["Do not separate only by timing; this combination needs professional review."],
  "disclaimer": "This is not medical advice. Consult a doctor or pharmacist."
}
```

`GET /interactions/history`

## AI Review Handoff

`POST /ai/safety-checks`

```json
{
  "request_source": "frontend"
}
```

`GET /ai/safety-checks/pending`

`GET /ai/safety-checks/{id}`

`PUT /ai/safety-checks/{id}/result`

```json
{
  "status": "completed",
  "aiResult": {
    "summary": "Plain-language AI review summary.",
    "warnings": [],
    "recommendedActions": [],
    "disclaimer": "This is not medical advice. Consult a doctor or pharmacist."
  }
}
```

The backend stores the AI result but does not implement the AI pipeline.

## Reminders

`POST /reminders`

```json
{
  "medicationId": "uuid",
  "time": "08:30",
  "repeatPattern": "daily",
  "timezone": "Europe/Berlin"
}
```

`GET /reminders/today`

`PUT /reminders/{id}`

`DELETE /reminders/{id}`

`POST /reminders/{id}/taken`

`POST /reminders/{id}/missed`

## Reports

`GET /reports/medication-summary`

`GET /emergency-card`

Returns a compact emergency medication card with patient summary, allergies, current medications, supplements, and high-priority warnings.

## Caregiver

`POST /caregiver/invite`

```json
{
  "caregiverEmail": "caregiver@example.com",
  "relationship": "daughter",
  "canManage": false,
  "missedDoseAlerts": true
}
```

`GET /caregiver/patients`

`GET /caregiver/patients/{id}/medications`

## Integrations And Languages

`POST /integrations`

```json
{
  "integrationType": "wearable",
  "providerName": "Starter Device",
  "externalReference": "optional-reference"
}
```

`GET /integrations`

`GET /localization/languages`
