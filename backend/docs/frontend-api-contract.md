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
  "password": "StrongPassword123!",
  "repeatPassword": "StrongPassword123!",
  "fullName": "Alex Patient",
  "role": "patient",
  "age": 35,
  "phoneNumber": "+1-555-0100",
  "termsConsent": true,
  "medicalDisclaimerConsent": true
}
```

Roles are `patient`, `caregiver`, `clinician`, and `admin`. Password rule: at least 8 characters with uppercase, lowercase, and a special character. Terms/privacy consent and medical disclaimer consent are required.

`POST /auth/login`

```json
{
  "email": "patient@example.com",
  "password": "StrongPassword123!"
}
```

`GET /auth/me`

`POST /auth/forgot-password`

```json
{
  "email": "patient@example.com"
}
```

Local/demo response includes a `reset_token` so the flow can be tested without email delivery.

`POST /auth/reset-password`

```json
{
  "token": "reset-token-from-forgot-password",
  "password": "NewStrong123!",
  "repeatPassword": "NewStrong123!"
}
```

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
  "caffeinePreworkoutUse": "none",
  "emergencyContactName": "Sam Patient",
  "emergencyContactPhone": "+1-555-0100"
}
```

## Dashboard

`GET /dashboard/summary`

`GET /dashboard/risk-summary`

Returns:

```json
{
  "total_medications": 2,
  "total_supplements": 1,
  "active_reminders_today": 1,
  "missed_doses_today": 0,
  "highest_current_risk_level": "high",
  "detected_interactions": 1,
  "next_medication_reminder": {
    "id": "uuid",
    "time": "08:30",
    "medication_id": "uuid",
    "medication_name": "Metformin"
  },
  "adherence_percentage": 85.0
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

`POST /medications/camera`

```json
{
  "imageData": "data:image/jpeg;base64,...",
  "fileName": "camera.jpg",
  "name": "Loratadine",
  "dosage": "10mg",
  "frequency": "daily"
}
```

`POST /medications/upload`

Send `multipart/form-data`:

```text
file=<image or PDF>
name=<optional medication name>
dosage=<optional dosage>
frequency=<optional frequency>
ocr_text=<optional OCR text>
```

These endpoints create a real medication immediately. Use scan endpoints only when the frontend wants a review draft first.

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

## Substances And Lifestyle Factors

Use this module for non-judgmental safety context beyond standard prescriptions. Birth control pills and emergency contraception should be tracked here or as medications because they can interact with antibiotics, St. John's Wort, vomiting/diarrhea situations, and enzyme-inducing medicines.

`POST /substances`

```json
{
  "name": "Birth control pills",
  "category": "hormonal_contraception",
  "activeIngredient": "ethinyl estradiol",
  "frequency": "daily",
  "amount": "1 tablet",
  "notes": "Optional notes",
  "isActive": true
}
```

Categories:

```text
alcohol, caffeine, nicotine, supplement, hormonal_contraception, OTC_medicine,
food_interaction, recreational_placeholder, other
```

Quick-select examples for the frontend:

- Alcohol
- Smoking/nicotine
- Caffeine or energy drinks
- Pre-workout supplements
- Herbal supplements such as St. John's Wort
- Birth control pills or emergency contraception
- Vitamins/minerals, protein, creatine
- Grapefruit or grapefruit juice
- OTC medicines such as ibuprofen, paracetamol/acetaminophen, cold/flu medicine, antihistamines
- Recreational substances placeholder

`GET /substances`

`PUT /substances/{id}`

`DELETE /substances/{id}`

## Safety

`POST /safety-check`

Analyzes medications, supplements, substances/lifestyle factors, and the user health profile.

Returns:

```json
{
  "total_risk_score": 50,
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

Seed rules include sleeping pill + alcohol, anxiety medication + alcohol, antibiotic + birth control, St. John's Wort + birth control, grapefruit + certain medications, high caffeine/pre-workout + anxiety medication, NSAID + alcohol, paracetamol/acetaminophen + alcohol, cold medicine + paracetamol duplication, and nicotine/smoking effects on some medications.

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

## Timeline, Adherence, Refills

`GET /timeline/today`

Returns today grouped by `morning`, `afternoon`, `evening`, and `night`.

`GET /adherence/summary`

Returns scheduled, taken, late, missed, adherence percentage, and weekly trend.

`GET /refills/due`

Returns medications where `pills_remaining <= refill_threshold`.

## Side Effects

`POST /side-effects`

```json
{
  "symptom": "nausea",
  "severity": "mild",
  "startedAt": "2026-06-27T09:00:00",
  "medicationId": "optional-medication-id",
  "notes": "Optional notes"
}
```

`GET /side-effects`

`GET /side-effects/summary`

Includes the safety note: `This does not diagnose side effects. Share this information with a doctor or pharmacist.`

## Assistant Placeholder

`POST /assistant/ask`

```json
{
  "question": "Can I drink alcohol tonight?"
}
```

Uses rule-based context only. It does not call an LLM API and does not diagnose.

## Sharing

`POST /share/report-link`

`GET /share/report/{token}`

Creates and reads a temporary read-only medication report link.

## Reports

`GET /reports/medication-summary`

`GET /emergency-card`

Returns a compact emergency medication card:

```json
{
  "user_name": "Alex Patient",
  "age": 70,
  "allergies": ["penicillin"],
  "conditions": ["atrial fibrillation"],
  "current_medications": [],
  "emergency_contact": {
    "name": "Sam Patient",
    "phone": "+1-555-0100",
    "email": "patient@example.com"
  },
  "highest_risk_warnings": [],
  "qr_code_placeholder": "QR code can link to this emergency card in a deployed app.",
  "disclaimer": "This is not medical advice. Consult a doctor or pharmacist."
}
```

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

`GET /caregiver/patients/{id}/reminders`

`GET /caregiver/patients/{id}/missed-doses`

`GET /caregiver/patients/{id}/report`

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
