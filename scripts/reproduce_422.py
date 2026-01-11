import requests
import json

def test_booking_error():
    url = "http://localhost:8000/api/v1/book-appointment"
    payload = {
        "first_name": "Kirti",
        "last_name": "Jullakanti",
        "dob": "1987-07-10",
        "insurance_provider": "MediBuddy",
        "reason": "Fever",
        "doctor_id": "DOC003",
        "requested_datetime": "2026-01-02T09:30:00"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to {url} as JSON...")
    response = requests.post(url, json=payload, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

if __name__ == "__main__":
    test_booking_error()
