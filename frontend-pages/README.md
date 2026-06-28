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

- `/register.html`
- `/login.html`
- `/auth.html` redirects to registration for backwards compatibility.
- `/profile.html`
- `/medications.html`
- `/scans.html`
- `/supplements.html`
- `/substances.html`
- `/safety.html`
- `/timeline.html`
- `/adherence.html`
- `/side-effects.html`
- `/assistant.html`
- `/ai-review.html`
- `/reminders.html`
- `/reports.html`
- `/emergency.html`
- `/caregiver.html`
- `/integrations.html`
- `/share.html`

API details are in `api-map.json` and `../backend/docs/frontend-api-contract.md`.

The main pages include `app.js`, a tiny working starter client:

- Register first on `register.html`, then MedGuard redirects to `login.html`.
- Register requires full name, email, password, repeat password, role, age, terms consent, and medical disclaimer consent.
- Passwords need at least 8 characters, uppercase, lowercase, and a special character.
- Use forgot/reset password forms on `login.html` for local reset-token testing.
- The JWT is stored in `localStorage` when "remember me" is checked, otherwise in `sessionStorage`.
- Add medicines manually on `medications.html`.
- Add medicines directly by camera or upload on `medications.html`.
- Add alcohol, caffeine, nicotine, birth control, grapefruit, OTC medicines, and lifestyle factors on `substances.html`.
- Create barcode, OCR, camera, or upload drafts on `scans.html`.
- Save a scan draft as a medication from the scan drafts table.
- Load dashboard metrics on `index.html`, run safety checks on `safety.html`, generate reports on `reports.html`, and print the emergency card on `emergency.html`.
- Use `timeline.html`, `adherence.html`, `side-effects.html`, `assistant.html`, and `share.html` as MVP handoff pages for the startup features.
