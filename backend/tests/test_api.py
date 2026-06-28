from fastapi.testclient import TestClient


def register(client: TestClient, email: str = "patient@example.com", role: str = "patient") -> dict:
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "StrongPassword123!",
            "repeat_password": "StrongPassword123!",
            "full_name": email.split("@")[0].title(),
            "role": role,
            "age": 35,
            "terms_consent": True,
            "medical_disclaimer_consent": True,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_root_points_to_docs(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"


def test_password_policy_and_reset_flow(client: TestClient) -> None:
    weak = client.post(
        "/auth/register",
        json={
            "email": "weak@example.com",
            "password": "password",
            "repeatPassword": "password",
            "fullName": "Weak Password",
            "role": "patient",
            "age": 35,
            "termsConsent": True,
            "medicalDisclaimerConsent": True,
        },
    )
    assert weak.status_code == 422

    mismatch = client.post(
        "/auth/register",
        json={
            "email": "mismatch@example.com",
            "password": "StrongPassword123!",
            "repeatPassword": "StrongPassword123?",
            "fullName": "Mismatch Password",
            "role": "patient",
            "age": 35,
            "termsConsent": True,
            "medicalDisclaimerConsent": True,
        },
    )
    assert mismatch.status_code == 422

    register(client, "reset@example.com")
    forgot = client.post("/auth/forgot-password", json={"email": "reset@example.com"})
    assert forgot.status_code == 200
    reset_token = forgot.json()["reset_token"]
    assert reset_token

    reset = client.post(
        "/auth/reset-password",
        json={
            "token": reset_token,
            "password": "NewStrong123!",
            "repeatPassword": "NewStrong123!",
        },
    )
    assert reset.status_code == 200
    assert reset.json()["access_token"]

    old_login = client.post("/auth/login", json={"email": "reset@example.com", "password": "StrongPassword123!"})
    assert old_login.status_code == 401

    new_login = client.post("/auth/login", json={"email": "reset@example.com", "password": "NewStrong123!"})
    assert new_login.status_code == 200


def test_auth_profile_medication_supplement_safety_report_flow(client: TestClient) -> None:
    token = register(client)["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile = client.put(
        "/profile",
        headers=headers,
        json={
            "age": 70,
            "sex": "male",
            "weight": 82,
            "known_conditions": ["atrial fibrillation"],
            "allergies": ["penicillin"],
            "alcohol_use": "occasional",
            "caffeine_preworkout_use": "none",
            "emergency_contact_name": "Sam Patient",
            "emergency_contact_phone": "+1-555-0100",
        },
    )
    assert profile.status_code == 200

    warfarin = client.post(
        "/medications",
        headers=headers,
        json={
            "name": "Warfarin",
            "active_ingredient": "warfarin",
            "dosage": "5mg",
            "form": "tablet",
            "frequency": "once daily",
            "medication_category": "blood thinner",
            "is_prescription": True,
        },
    )
    assert warfarin.status_code == 201

    ibuprofen = client.post(
        "/medications",
        headers=headers,
        json={
            "name": "Ibuprofen",
            "active_ingredient": "ibuprofen",
            "dosage": "200mg",
            "form": "tablet",
            "frequency": "as needed",
            "medication_category": "nsaid",
            "is_prescription": False,
        },
    )
    assert ibuprofen.status_code == 201

    supplement = client.post(
        "/supplements",
        headers=headers,
        json={
            "name": "Pre-workout",
            "active_ingredient_category": "caffeine",
            "dose": "1 scoop",
            "frequency": "before exercise",
        },
    )
    assert supplement.status_code == 201

    safety = client.post("/safety-check", headers=headers, json={})
    assert safety.status_code == 200
    safety_data = safety.json()
    assert safety_data["total_risk_score"] > 0
    assert safety_data["highest_severity"] in {"high", "critical"}
    assert safety_data["disclaimer"] == "This is not medical advice. Consult a doctor or pharmacist."

    history = client.get("/interactions/history", headers=headers)
    assert history.status_code == 200
    assert len(history.json()) == 1

    report = client.get("/reports/medication-summary", headers=headers)
    assert report.status_code == 200
    assert len(report.json()["current_medications"]) == 2
    assert len(report.json()["supplements"]) == 1
    assert "recommendations" in report.json()
    assert "generated_date" in report.json()

    dashboard = client.get("/dashboard/summary", headers=headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["total_medications"] == 2
    assert dashboard.json()["total_supplements"] == 1
    assert dashboard.json()["detected_interactions"] >= 1


def test_frontend_style_medication_and_supplement_payloads(client: TestClient) -> None:
    token = register(client, "frontend@example.com")["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    medication = client.post(
        "/medications",
        headers=headers,
        json={
            "name": "Vitamin D",
            "activeIngredient": "",
            "dosage": "",
            "form": "Tablet",
            "frequency": "",
            "startDate": "2026-06-27",
            "medicationCategory": "vitamin",
            "isPrescription": False,
        },
    )
    assert medication.status_code == 201
    medication_data = medication.json()
    assert medication_data["active_ingredient"] == "Vitamin D"
    assert medication_data["dosage"] == "confirm with label"
    assert medication_data["frequency"] == "as directed"
    assert medication_data["form"] == "tablet"
    assert medication_data["is_prescription"] is False

    supplement = client.post(
        "/supplements",
        headers=headers,
        json={
            "name": "Creatine",
            "activeIngredientCategory": "creatine monohydrate",
            "dose": "5g",
            "frequency": "daily",
        },
    )
    assert supplement.status_code == 201

    detail = client.get(f"/supplements/{supplement.json()['id']}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["active_ingredient_category"] == "creatine monohydrate"


def test_substances_crud_and_safety_rules(client: TestClient) -> None:
    token = register(client, "substances@example.com")["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    sleeping_pill = client.post(
        "/medications",
        headers=headers,
        json={
            "name": "Zolpidem",
            "activeIngredient": "zolpidem",
            "dosage": "5mg",
            "form": "tablet",
            "frequency": "nightly",
            "medicationCategory": "sleeping pill",
        },
    )
    assert sleeping_pill.status_code == 201

    alcohol = client.post(
        "/substances",
        headers=headers,
        json={"name": "Alcohol", "category": "alcohol", "frequency": "occasionally", "amount": "1 drink"},
    )
    assert alcohol.status_code == 201
    assert alcohol.json()["category"] == "alcohol"

    birth_control = client.post(
        "/substances",
        headers=headers,
        json={
            "name": "Birth control pills",
            "category": "hormonal_contraception",
            "activeIngredient": "ethinyl estradiol",
            "frequency": "daily",
        },
    )
    assert birth_control.status_code == 201

    st_johns = client.post(
        "/substances",
        headers=headers,
        json={
            "name": "St. John's Wort",
            "category": "supplement",
            "activeIngredient": "hypericum",
            "frequency": "daily",
        },
    )
    assert st_johns.status_code == 201

    listed = client.get("/substances", headers=headers)
    assert listed.status_code == 200
    assert {item["name"] for item in listed.json()} >= {"Alcohol", "Birth control pills", "St. John's Wort"}

    updated = client.put(
        f"/substances/{alcohol.json()['id']}",
        headers=headers,
        json={"amount": "2 drinks", "notes": "weekends"},
    )
    assert updated.status_code == 200
    assert updated.json()["amount"] == "2 drinks"

    safety = client.post("/safety-check", headers=headers, json={})
    assert safety.status_code == 200
    safety_data = safety.json()
    assert safety_data["highest_severity"] == "critical"
    explanations = " ".join(item["explanation"] for item in safety_data["interactions"])
    assert "Alcohol with sleeping pills" in explanations
    assert "St. John's Wort" in explanations
    assert safety_data["disclaimer"] == "This is not medical advice. Consult a doctor or pharmacist."

    deleted = client.delete(f"/substances/{st_johns.json()['id']}", headers=headers)
    assert deleted.status_code == 204


def test_scan_ai_history_emergency_and_integration_starters(client: TestClient) -> None:
    token = register(client, "features@example.com")["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    medication = client.post(
        "/medications",
        headers=headers,
        json={
            "name": "Warfarin",
            "activeIngredient": "warfarin",
            "dosage": "5mg",
            "form": "tablet",
            "frequency": "daily",
            "medicationCategory": "blood thinner",
        },
    )
    assert medication.status_code == 201

    barcode = client.post(
        "/scans/barcode",
        headers=headers,
        json={
            "barcode": "0123456789012",
            "productName": "Ibuprofen",
            "activeIngredient": "ibuprofen",
            "dosage": "200mg",
        },
    )
    assert barcode.status_code == 201
    assert barcode.json()["medication_draft"]["name"] == "Ibuprofen"

    ocr = client.post(
        "/scans/prescription-ocr",
        headers=headers,
        json={"ocrText": "Amoxicillin\n500mg capsule"},
    )
    assert ocr.status_code == 201
    assert ocr.json()["scan_type"] == "prescription_ocr"

    camera = client.post(
        "/scans/camera",
        headers=headers,
        json={"imageData": "data:image/png;base64,abc123", "fileName": "package.png"},
    )
    assert camera.status_code == 201
    assert camera.json()["scan_type"] == "camera"

    upload = client.post(
        "/scans/upload",
        headers=headers,
        data={"ocr_text": "Cetirizine\n10mg tablet"},
        files={"file": ("prescription.png", b"fake-image", "image/png")},
    )
    assert upload.status_code == 201
    assert upload.json()["scan_type"] == "upload"

    from_scan = client.post(
        f"/scans/{upload.json()['id']}/medication",
        headers=headers,
        json={"frequency": "once daily"},
    )
    assert from_scan.status_code == 201
    assert from_scan.json()["name"] == "Cetirizine"

    ai_review = client.post("/ai/safety-checks", headers=headers, json={"request_source": "test"})
    assert ai_review.status_code == 201
    review_id = ai_review.json()["id"]
    assert ai_review.json()["status"] == "pending"
    assert "rule_based_safety_result" in ai_review.json()["input_snapshot"]

    ai_result = client.put(
        f"/ai/safety-checks/{review_id}/result",
        headers=headers,
        json={"status": "completed", "aiResult": {"summary": "No extra AI warning in test."}},
    )
    assert ai_result.status_code == 200
    assert ai_result.json()["status"] == "completed"

    history = client.get("/medications/history", headers=headers)
    assert history.status_code == 200
    assert "adherence_rate_percent" in history.json()["adherence_summary"]

    emergency = client.get("/emergency-card", headers=headers)
    assert emergency.status_code == 200
    assert emergency.json()["user_name"] == "Features"
    assert emergency.json()["emergency_contact"]["email"] == "features@example.com"

    integration = client.post(
        "/integrations",
        headers=headers,
        json={"integrationType": "wearable", "providerName": "Starter Device"},
    )
    assert integration.status_code == 201
    assert integration.json()["integration_type"] == "wearable"

    languages = client.get("/localization/languages", headers=headers)
    assert languages.status_code == 200
    assert languages.json()[0]["code"] == "en"


def test_direct_camera_and_upload_create_medications(client: TestClient) -> None:
    token = register(client, "upload@example.com")["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    upload = client.post(
        "/medications/upload",
        headers=headers,
        data={"name": "Paracetamol", "dosage": "500mg", "frequency": "as needed"},
        files={"file": ("medicine.png", b"fake-image", "image/png")},
    )
    assert upload.status_code == 201
    assert upload.json()["name"] == "Paracetamol"
    assert upload.json()["active_ingredient"] == "Paracetamol"

    camera = client.post(
        "/medications/camera",
        headers=headers,
        json={
            "imageData": "data:image/jpeg;base64,abc123",
            "fileName": "camera.jpg",
            "name": "Loratadine",
            "dosage": "10mg",
            "frequency": "daily",
        },
    )
    assert camera.status_code == 201
    assert camera.json()["name"] == "Loratadine"

    medications = client.get("/medications", headers=headers)
    assert medications.status_code == 200
    assert {med["name"] for med in medications.json()} == {"Loratadine", "Paracetamol"}


def test_reminder_and_adherence_flow(client: TestClient) -> None:
    token = register(client, "reminders@example.com")["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    medication = client.post(
        "/medications",
        headers=headers,
        json={
            "name": "Metformin",
            "active_ingredient": "metformin",
            "dosage": "500mg",
            "form": "tablet",
            "frequency": "twice daily",
            "is_prescription": True,
        },
    ).json()

    reminder = client.post(
        "/reminders",
        headers=headers,
        json={"medication_id": medication["id"], "time": "08:30", "repeat_pattern": "daily"},
    )
    assert reminder.status_code == 201
    reminder_id = reminder.json()["id"]

    taken = client.post(f"/reminders/{reminder_id}/taken", headers=headers, json={})
    assert taken.status_code == 200
    assert taken.json()["status"] in {"taken", "late"}

    today = client.get("/reminders/today", headers=headers)
    assert today.status_code == 200
    assert today.json()[0]["taken_status"] is True or taken.json()["status"] == "late"


def test_startup_mvp_endpoints(client: TestClient) -> None:
    token = register(client, "startup@example.com")["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    medication = client.post(
        "/medications",
        headers=headers,
        json={
            "name": "Ibuprofen",
            "activeIngredient": "ibuprofen",
            "dosage": "200mg",
            "form": "tablet",
            "frequency": "as needed",
            "medicationCategory": "nsaid",
            "isPrescription": False,
            "pillsRemaining": 3,
            "pillsPerDose": 1,
            "refillThreshold": 5,
            "pharmacyName": "Campus Pharmacy",
        },
    )
    assert medication.status_code == 201
    med_id = medication.json()["id"]

    reminder = client.post(
        "/reminders",
        headers=headers,
        json={"medicationId": med_id, "time": "23:59", "repeatPattern": "daily"},
    )
    assert reminder.status_code == 201

    alcohol = client.post(
        "/substances",
        headers=headers,
        json={"name": "Alcohol", "category": "alcohol", "frequency": "occasionally"},
    )
    assert alcohol.status_code == 201

    risk = client.get("/dashboard/risk-summary", headers=headers)
    assert risk.status_code == 200
    assert risk.json()["total_medications"] == 1
    assert risk.json()["total_substances"] == 1
    assert "disclaimer" in risk.json()

    timeline = client.get("/timeline/today", headers=headers)
    assert timeline.status_code == 200
    assert set(timeline.json().keys()) == {"morning", "afternoon", "evening", "night"}

    adherence = client.get("/adherence/summary", headers=headers)
    assert adherence.status_code == 200
    assert "weekly_trend" in adherence.json()

    refills = client.get("/refills/due", headers=headers)
    assert refills.status_code == 200
    assert refills.json()[0]["name"] == "Ibuprofen"

    side_effect = client.post(
        "/side-effects",
        headers=headers,
        json={"symptom": "nausea", "severity": "mild", "medicationId": med_id},
    )
    assert side_effect.status_code == 201

    side_summary = client.get("/side-effects/summary", headers=headers)
    assert side_summary.status_code == 200
    assert side_summary.json()["total_logs"] == 1
    assert "does not diagnose" in side_summary.json()["note"]

    assistant = client.post("/assistant/ask", headers=headers, json={"question": "Can I drink alcohol tonight?"})
    assert assistant.status_code == 200
    assert assistant.json()["disclaimer"] == "This is not medical advice. Consult a doctor or pharmacist."

    assistant_status = client.get("/assistant/status", headers=headers)
    assert assistant_status.status_code == 200
    assert "connected" in assistant_status.json()
    assert assistant_status.json()["fallback"] == "rule_based_safety_engine"

    share = client.post("/share/report-link", headers=headers, json={"expiresInHours": 24})
    assert share.status_code == 201
    shared = client.get(f"/share/report/{share.json()['token']}")
    assert shared.status_code == 200
    assert shared.json()["report"]["current_medications"][0]["name"] == "Ibuprofen"


def test_caregiver_can_view_patient_medications(client: TestClient) -> None:
    patient = register(client, "care-patient@example.com")
    caregiver = register(client, "caregiver@example.com", role="caregiver")
    patient_headers = {"Authorization": f"Bearer {patient['access_token']}"}
    caregiver_headers = {"Authorization": f"Bearer {caregiver['access_token']}"}

    med = client.post(
        "/medications",
        headers=patient_headers,
        json={
            "name": "Amlodipine",
            "active_ingredient": "amlodipine",
            "dosage": "5mg",
            "form": "tablet",
            "frequency": "daily",
            "is_prescription": True,
        },
    )
    assert med.status_code == 201

    invite = client.post(
        "/caregiver/invite",
        headers=patient_headers,
        json={"caregiver_email": "caregiver@example.com", "relationship": "daughter", "can_manage": False},
    )
    assert invite.status_code == 201

    patients = client.get("/caregiver/patients", headers=caregiver_headers)
    assert patients.status_code == 200
    patient_id = patients.json()[0]["id"]

    meds = client.get(f"/caregiver/patients/{patient_id}/medications", headers=caregiver_headers)
    assert meds.status_code == 200
    assert meds.json()[0]["name"] == "Amlodipine"

    reminders = client.get(f"/caregiver/patients/{patient_id}/reminders", headers=caregiver_headers)
    assert reminders.status_code == 200

    missed = client.get(f"/caregiver/patients/{patient_id}/missed-doses", headers=caregiver_headers)
    assert missed.status_code == 200

    report = client.get(f"/caregiver/patients/{patient_id}/report", headers=caregiver_headers)
    assert report.status_code == 200
    assert report.json()["current_medications"][0]["name"] == "Amlodipine"


def test_invalid_reminder_time_rejected(client: TestClient) -> None:
    token = register(client, "bad-reminder@example.com")["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    medication = client.post(
        "/medications",
        headers=headers,
        json={
            "name": "Medication",
            "active_ingredient": "ingredient",
            "dosage": "1 tablet",
            "form": "tablet",
            "frequency": "daily",
        },
    ).json()

    response = client.post(
        "/reminders",
        headers=headers,
        json={"medication_id": medication["id"], "time": "29:99", "repeat_pattern": "daily"},
    )
    assert response.status_code == 422
