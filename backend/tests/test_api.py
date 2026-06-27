from fastapi.testclient import TestClient


def register(client: TestClient, email: str = "patient@example.com", role: str = "patient") -> dict:
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "StrongPassword123",
            "full_name": email.split("@")[0].title(),
            "role": role,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_root_points_to_docs(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"


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


def test_frontend_style_medication_and_supplement_payloads(client: TestClient) -> None:
    token = register(client, "frontend@example.com")["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    medication = client.post(
        "/medications",
        headers=headers,
        json={
            "name": "Vitamin D",
            "activeIngredient": "",
            "dosage": "1000 IU",
            "form": "Tablet",
            "frequency": "daily",
            "startDate": "2026-06-27",
            "medicationCategory": "vitamin",
            "isPrescription": False,
        },
    )
    assert medication.status_code == 201
    medication_data = medication.json()
    assert medication_data["active_ingredient"] == "Vitamin D"
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
    assert taken.json()["status"] == "taken"

    today = client.get("/reminders/today", headers=headers)
    assert today.status_code == 200
    assert today.json()[0]["taken_status"] is True


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
