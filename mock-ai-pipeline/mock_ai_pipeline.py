import argparse
import os
import time

import requests
from requests.exceptions import ConnectionError, HTTPError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mock MedGuard safety-check pipeline trigger")
    parser.add_argument("--base-url", default=os.getenv("MEDGUARD_API_BASE_URL", "http://127.0.0.1:8000/api/v1"))
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--poll", action="store_true")
    parser.add_argument("--interval", type=int, default=10)
    return parser.parse_args()


def login(base_url: str, email: str, password: str) -> str:
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            json={"email": email, "password": password},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except ConnectionError:
        print(f"Could not connect to the backend at {base_url}.")
        print("Start the backend first:")
        print("cd backend")
        print(r".\start-local-sqlite.ps1")
        raise SystemExit(1)
    except HTTPError as exc:
        if exc.response.status_code == 401:
            print("Login failed. Create demo users first:")
            print("cd demo-seed")
            print("python seed_demo.py")
            raise SystemExit(1)
        print(f"Backend returned {exc.response.status_code} for {exc.response.url}.")
        print(exc.response.text)
        raise SystemExit(1)


def run_safety_check(base_url: str, token: str) -> None:
    response = requests.post(
        f"{base_url}/safety-check",
        headers={"Authorization": f"Bearer {token}"},
        json={},
        timeout=15,
    )
    response.raise_for_status()
    result = response.json()
    print(
        "Safety check completed: "
        f"score={result['total_risk_score']} "
        f"highest={result.get('highest_severity')} "
        f"interactions={len(result['interactions'])}"
    )


def main() -> None:
    args = parse_args()
    base_url = args.base_url.rstrip("/")
    token = login(base_url, args.email, args.password)
    print("Logged in. Mock safety pipeline trigger ready.")

    while True:
        run_safety_check(base_url, token)
        if not args.poll:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
