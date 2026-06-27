import requests

BASE_URL = "http://127.0.0.1:8000"


def create_ai_review(access_token: str) -> dict:
    response = requests.post(
        f"{BASE_URL}/ai/safety-checks",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"request_source": "ai-service"},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def submit_ai_result(access_token: str, review_id: str, result: dict) -> dict:
    response = requests.put(
        f"{BASE_URL}/ai/safety-checks/{review_id}/result",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "status": "completed",
            "aiResult": {
                **result,
                "disclaimer": "This is not medical advice. Consult a doctor or pharmacist.",
            },
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    print("Import create_ai_review() and submit_ai_result() from this starter file.")
