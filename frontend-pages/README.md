# MedGuard Frontend Pages

This folder is a frontend handoff starter, not a finished UI framework. It gives the frontend team the screens, form fields, and API endpoints that the backend supports.

Run locally with any static file server:

```bash
python -m http.server 3000
```

Then open:

```text
http://127.0.0.1:3000
```

The backend should be running separately at:

```text
http://127.0.0.1:8000
```

Recommended frontend routes:

- `/auth.html`
- `/profile.html`
- `/medications.html`
- `/scans.html`
- `/supplements.html`
- `/safety.html`
- `/ai-review.html`
- `/reminders.html`
- `/reports.html`
- `/emergency.html`
- `/caregiver.html`
- `/integrations.html`

API details are in `api-map.json` and `../backend/docs/frontend-api-contract.md`.

`auth.html`, `medications.html`, and `scans.html` include `app.js`, a tiny working starter client:

- Register or log in on `auth.html`.
- The JWT is stored in `localStorage` as `medguardToken`.
- Add medicines manually on `medications.html`.
- Create barcode, OCR, camera, or upload drafts on `scans.html`.
- Save a scan draft as a medication from the scan drafts table.
