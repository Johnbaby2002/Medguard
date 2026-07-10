# MedGuard

**AI-Powered Medication Safety Assistant**

MedGuard is a medication safety support platform designed to help users manage medications, supplements, lifestyle factors, reminders, and interaction risks in one place. The project is built as a university MVP and focuses on medication safety awareness, adherence support, caregiver access, and doctor-ready reporting.

MedGuard does not diagnose, prescribe, or replace doctors or pharmacists. It provides safety support and clear warnings that should be discussed with a healthcare professional.

## Team

| Role | Team Member |
|---|---|
| Frontend | Artem Lisniakov |
| Backend | John Baby Nayathodan |
| AI | Joyel Raju |
| Business Lead | Khadija Mahmoud |

## Problem

Many people take multiple medications at the same time. They may also use over-the-counter medicines, supplements, alcohol, caffeine, nicotine, birth control, herbal products, or other lifestyle substances. These combinations can create safety risks that are easy to miss.

Common problems MedGuard addresses:

- Users forget what medicines they take or when they took them.
- Users may not know that medicines can interact with food, supplements, alcohol, or other medicines.
- Doctors and pharmacists need a clear medication list to give better advice.
- Caregivers may need a simple way to help patients track medication routines.
- Medication safety information is often difficult for users to understand.

## Solution

MedGuard gives users a simple digital place to record their health profile, medications, supplements, and lifestyle factors. The app then checks for rule-based safety risks and explains them in plain language.

The goal is not to replace professional medical advice. The goal is to help users become more organized, more informed, and better prepared when speaking with a doctor or pharmacist.

## How MedGuard Works

1. **Create a health profile**

   Users can record basic health information such as age, allergies, known conditions, pregnancy status, alcohol use, caffeine use, and emergency contact details.

2. **Add medications**

   Users can add prescription medicines, over-the-counter medicines, dosage, frequency, form, prescribing doctor, notes, refill details, and schedule information.

3. **Add supplements and lifestyle factors**

   Users can track items such as vitamins, protein, creatine, herbal products, alcohol, caffeine, energy drinks, nicotine, birth control, grapefruit, painkillers, cold medicine, and antihistamines.

4. **Run a safety check**

   MedGuard analyzes the user's medication list, supplements, lifestyle factors, and health profile using a rule-based safety engine.

5. **Receive simple results**

   The app returns a risk score, warning level, plain-language explanation, safety recommendation, and medical disclaimer.

6. **Track reminders and reports**

   Users can create reminders, mark doses as taken or missed, view adherence summaries, and generate doctor-ready medication reports.

## Main Features

- User registration and login
- Secure password hashing and token-based authentication
- Personal health profile
- Medication management
- Supplement management
- Substances and lifestyle tracking
- Rule-based medication safety analysis
- Interaction risk score
- Plain-language safety explanations
- Smart medication reminders
- Missed-dose tracking
- Medication timeline
- Refill reminder support
- Side effect logging
- Emergency medication card
- Doctor-ready medication summary report
- Caregiver support
- Organization-ready structure for future clinic or pharmacy use
- AI pipeline starter for future AI integration

## Example Safety Cases

MedGuard includes starter safety rules for common medication and lifestyle risks, such as:

- Blood thinner with NSAID painkiller may increase bleeding risk.
- Sleeping pill with alcohol may cause dangerous sedation.
- Anxiety medication with sleeping pill may increase drowsiness and fall risk.
- Antibiotics with birth control may reduce contraceptive effectiveness in some cases.
- St. John's Wort with birth control may reduce contraceptive effectiveness.
- Grapefruit with certain medicines may increase drug levels.
- High caffeine or pre-workout with anxiety medication may increase heart rate and nervousness.
- Paracetamol or acetaminophen with alcohol may increase liver risk.
- Multiple cold medicines with the same ingredient may increase overdose risk.

These examples are for MVP demonstration and are not a complete clinical interaction database.

## Technology Stack

**Backend**

- FastAPI
- Python
- SQLAlchemy
- SQLite for local prototype use
- PostgreSQL-ready database configuration
- JWT authentication
- Pydantic validation

**Frontend**

- HTML, CSS, and JavaScript handoff pages
- React/Vite frontend structure may also be used by the frontend team, depending on the active branch/version

**AI**

- Local AI pipeline starter
- Rule-based assistant fallback
- Designed so the AI team can connect a future model without changing the core backend structure

## Project Structure

```text
Medguard/
  backend/          FastAPI backend, database models, services, safety engine
  frontend-pages/   HTML/CSS/JS handoff pages for frontend integration
  ai-pipeline/      Local AI pipeline starter
  ai-starter/       AI integration contract and example client
  scripts/          Easy setup, run, and test commands
```

Some versions of the project may also include a `frontend/` folder for the React/Vite frontend.

## Quick Start

Use these commands from the project root:

```bash
cd Medguard
npm install
npm run setup
npm run dev
```

Open the app locally:

```text
Frontend: http://127.0.0.1:3000
Backend docs: http://127.0.0.1:8000/docs
```

Useful commands:

```bash
npm run backend
npm run frontend
npm run test
```

## Requirements

- Node.js 18 or newer
- Python 3.11 or newer
- Git

Docker is optional. The default local setup uses SQLite so teammates can run the project quickly without installing PostgreSQL.

## Database

For local development, MedGuard uses SQLite because it is simple and easy for teammates to run.

For a more production-like setup, the backend is prepared for PostgreSQL. This makes the architecture easier to extend later for clinics, pharmacies, or other organization-based use cases.

## Testing

Run the backend test suite with:

```bash
npm run test
```

The tests check the main backend flows such as authentication, medication management, safety checks, reminders, reports, caregiver access, substances, side effects, and sharing features.

## Safety and Medical Disclaimer

MedGuard is a medication safety support tool. It is not a medical device and does not replace a doctor, pharmacist, or emergency service.

Always include this disclaimer with safety-related results:

```text
This is not medical advice. Consult a doctor or pharmacist.
```

Users should not start, stop, or change medication based only on MedGuard. Any warning or recommendation should be discussed with a qualified healthcare professional.

## Current MVP Limitations

- The safety engine uses starter rule-based examples, not a complete medical database.
- The AI assistant is a placeholder/starter and should not be treated as a clinical AI system.
- OCR, barcode scanning, predictive risk analysis, EHR integration, wearable integration, and multilingual support are future features.
- The current app is intended for prototype demonstration and academic project work.

## Future Improvements

- OCR prescription scanning
- Barcode medicine scanning
- More complete clinical interaction database
- Real AI assistant integration
- Multi-language support
- Emergency medication card sharing
- Wearable integration
- EHR integration
- Pharmacy and insurance integration
- B2B clinic/pharmacy dashboard

## Summary

MedGuard helps users organize medication information, understand possible interaction risks, remember doses, and prepare clearer reports for healthcare professionals. It combines medication management, lifestyle tracking, safety warnings, reminders, reports, caregiver support, and future AI integration in one MVP-ready platform.
