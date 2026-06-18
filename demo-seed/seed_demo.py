import os

import requests
from requests.exceptions import ConnectionError, HTTPError

BASE_URL = os.getenv("MEDGUARD_API_BASE_URL", "http://127.0.0.1:8000/api/v1")
PASSWORD = "StrongPassword123"


def post(path: str, payload: dict, token: str | None = None) -> dict:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.post(f"{BASE_URL}{path}", json=payload, headers=headers, timeout=15)
    if response.status_code == 409:
        return login(payload["email"], payload.get("password", PASSWORD))
    response.raise_for_status()
    return response.json()


def login(email: str, password: str = PASSWORD) -> dict:
    response = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password}, timeout=15)
    response.raise_for_status()
    return response.json()


def register(email: str, full_name: str, role: str) -> dict:
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": email, "password": PASSWORD, "full_name": full_name, "role": role},
        timeout=15,
    )
    if response.status_code == 409:
        return login(email)
    response.raise_for_status()
    return response.json()


def main() -> None:
    try:
        patient = register("patient@example.com", "Alex Patient", "patient")
        register("caregiver@example.com", "Casey Caregiver", "caregiver")
        token = patient["access_token"]

        warfarin = post(
            "/medications",
            {
                "name": "Warfarin",
                "active_ingredient": "warfarin",
                "dosage": "5mg",
                "form": "tablet",
                "frequency": "once daily",
                "medication_category": "blood thinner",
                "is_prescription": True,
                "notes": "Take once daily in the evening",
            },
            token,
        )
        post(
            "/medications",
            {
                "name": "Ibuprofen",
                "active_ingredient": "ibuprofen",
                "dosage": "200mg",
                "form": "tablet",
                "frequency": "as needed",
                "medication_category": "nsaid",
                "is_prescription": False,
                "notes": "Take only if approved by a clinician",
            },
            token,
        )
        post(
            "/supplements",
            {
                "name": "Pre-workout",
                "active_ingredient_category": "caffeine",
                "dose": "1 scoop",
                "frequency": "before gym",
                "notes": "High caffeine supplement",
            },
            token,
        )
        reminder = post(
            "/reminders",
            {
                "medication_id": warfarin["id"],
                "time": "08:30",
                "repeat_pattern": "daily",
                "timezone": "Europe/Berlin",
            },
            token,
        )
        post(
            f"/reminders/{reminder['id']}/taken",
            {},
            token,
        )
        post("/safety-check", {}, token)
        post(
            "/caregiver/invite",
            {
                "caregiver_email": "caregiver@example.com",
                "relationship": "family caregiver",
                "can_manage": False,
                "missed_dose_alerts": True,
            },
            token,
        )
    except ConnectionError:
        print("Could not connect to the backend at http://127.0.0.1:8000.")
        print("Start the backend first. Easiest local option:")
        print("cd backend")
        print(r".\start-local-sqlite.ps1")
        raise SystemExit(1)
    except HTTPError as exc:
        response = exc.response
        print(f"Backend returned {response.status_code} for {response.url}.")
        print("Backend response:")
        print(response.text)
        print("")
        print("If this happened during register/login, restart the backend after reinstalling requirements:")
        print("cd backend")
        print(r".\start-local-sqlite.ps1")
        raise SystemExit(1)

    print("Demo data created.")
    print("patient@example.com / StrongPassword123")
    print("caregiver@example.com / StrongPassword123")


if __name__ == "__main__":
    main()
