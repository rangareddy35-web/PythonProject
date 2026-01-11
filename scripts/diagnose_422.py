import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def diagnose_422():
    payload = {
        "first_name": "Kirti",
        "last_name": "Jullakanti",
        "dob": "1987-06-10",
        "insurance_provider": "Medibody",
        "reason": "General Pediatrics",
        "requested_datetime": "2025-01-26T21:30:00",
        "doctor_id": "DOC003"
    }

    print("--- Test 1: Content-Type: application/x-www-form-urlencoded ---")
    resp = requests.post(f"{BASE_URL}/book-appointment", data=payload)
    print(f"Status: {resp.status_code}")
    print(resp.json().get('message', resp.text))

    print("\n--- Test 2: Content-Type: text/plain ---")
    resp = requests.post(f"{BASE_URL}/book-appointment", data=json.dumps(payload), headers={"Content-Type": "text/plain"})
    print(f"Status: {resp.status_code}")
    print(resp.json().get('message', resp.text))

    print("\n--- Test 3: Missing Body ---")
    resp = requests.post(f"{BASE_URL}/book-appointment", headers={"Content-Type": "application/json"})
    print(f"Status: {resp.status_code}")
    print(resp.json().get('message', resp.text))

if __name__ == "__main__":
    diagnose_422()
