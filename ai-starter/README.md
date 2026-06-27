# MedGuard AI Starter

This folder is a handoff starter for the AI teammate. It does not implement the AI pipeline.

The backend already exposes safe handoff endpoints:

- `POST /ai/safety-checks` creates a pending AI review with a snapshot of the user's profile, medications, supplements, and rule-based safety result.
- `GET /ai/safety-checks/pending` lists pending reviews for the authenticated user.
- `GET /ai/safety-checks/{id}` returns one review and its input snapshot.
- `PUT /ai/safety-checks/{id}/result` lets the AI service submit a structured result.

The AI service should call backend APIs instead of reading or writing directly to the database.

Required safety rules:

- Do not diagnose disease.
- Do not replace doctors or pharmacists.
- Explain uncertainty plainly.
- Keep recommendations conservative.
- Always include: `This is not medical advice. Consult a doctor or pharmacist.`

Local backend URL:

```text
http://127.0.0.1:8000
```
