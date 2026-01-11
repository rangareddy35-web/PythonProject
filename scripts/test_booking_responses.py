import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_responses():
    # 1. Test Past Date Error (doctor_id in query)
    print("\n--- Testing Past Date Error (doctor_id in query) ---")
    payload = {
        "first_name": "Test",
        "last_name": "User",
        "dob": "1990-01-01",
        "insurance_provider": "TestInc",
        "reason": "Test",
        "requested_datetime": "2020-01-01T10:00:00"
    }
    resp = requests.post(f"{BASE_URL}/book-appointment?doctor_id=DOC001", json=payload)
    print(f"Status: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2))

    # 2. Test Success Pathway (using a future slot from the DB if possible, or just checking 409/400 logic)
    # Since I don't know the exact future slots easily without querying, I'll test the "No Slot" path carefully.
    print("\n--- Testing Slot Unavailable (Conversational) ---")
    payload_no_slot = {
        "first_name": "Test",
        "last_name": "User",
        "dob": "1990-01-01",
        "insurance_provider": "TestInc",
        "reason": "Test",
        "requested_datetime": "2026-12-11T12:34:56"
    }
    resp = requests.post(f"{BASE_URL}/book-appointment?doctor_id=DOC001", json=payload_no_slot)
    print(f"Status: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2))

if __name__ == "__main__":
    test_responses()
