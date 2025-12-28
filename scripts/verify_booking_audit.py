import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def get_doctors(dept=None):
    url = f"{BASE_URL}/available-slots"
    if dept:
        url += f"?department={dept}"
    resp = requests.get(url)
    return resp.json()

def book_appointment(data):
    resp = requests.post(f"{BASE_URL}/book-appointment", json=data)
    print(f"Book response status: {resp.status_code}")
    if resp.status_code != 200:
        print(resp.text)
    return resp.json()

def cancel_appointment(appt_id):
    resp = requests.post(f"{BASE_URL}/cancel-appointment", json={"appointment_id": appt_id})
    print(f"Cancel response status: {resp.status_code}")
    if resp.status_code != 200:
        print(resp.text)
    return resp.json()

def check_audit_log(appt_id):
    # Use the API endpoint
    try:
        resp = requests.get(f"{BASE_URL}/audit-logs")
        if resp.status_code == 200:
            logs = resp.json().get("logs", [])
            matching = [l for l in logs if l.get("appointment_id") == appt_id or l.get("appointment_id") == str(appt_id)]
            return matching
        return []
    except Exception as e:
        print(f"Could not read audit log: {e}")
        return []

def main():
    print("--- Starting Verification ---")
    
    # 1. Find a slot
    print("\n1. Finding slot for Cardiology...")
    docs = get_doctors("Cardiology")
    if not docs["doctors"]:
        print("No doctors found!")
        return

    doctor = docs["doctors"][0]
    if not doctor["available_slots"]:
        print("No slots available!")
        return
    
    slot = doctor["available_slots"][0]
    print(f"Found slot: {doctor['name']} at {slot['date']} {slot['time']}")
    
    requested_datetime = f"{slot['date']}T{slot['time']}:00"
    
    # 2. Book it
    print(f"\n2. Booking for {requested_datetime}...")
    book_payload = {
        "doctor_id": doctor["id"],
        "first_name": "Test",
        "last_name": "User",
        "dob": "1990-01-01",
        "insurance_provider": "TestIns",
        "reason": "Test",
        "requested_datetime": requested_datetime
    }
    
    book_resp = book_appointment(book_payload)
    if book_resp.get("status") != "booked":
        print("Booking failed!")
        return
    
    appt_id = book_resp["appointment"]["id"]
    print(f"Booked appointment ID: {appt_id}")
    
    # 3. Verify slot is gone
    print("\n3. Verifying slot is now booked...")
    docs_after = get_doctors("Cardiology")
    doc_after = next((d for d in docs_after["doctors"] if d["id"] == doctor["id"]), None)
    
    slot_exists = False
    for s in doc_after["available_slots"]:
        if s["date"] == slot["date"] and s["time"] == slot["time"]:
            slot_exists = True
            break
    
    if slot_exists:
        print("ERROR: Slot still appears as available!")
    else:
        print("SUCCESS: Slot is no longer listed as available.")

    # 4. Check Audit Log (Book)
    print("\n4. Checking Audit Log for BOOK action...")
    logs = check_audit_log(appt_id)
    book_logs = [l for l in logs if l["action"] == "BOOK"]
    if book_logs:
        print("SUCCESS: Found booking audit log.")
    else:
        print("ERROR: No booking audit log found.")

    # 5. Cancel Appointment
    print(f"\n5. Cancelling appointment {appt_id}...")
    cancel_resp = cancel_appointment(appt_id)
    if cancel_resp.get("status") != "cancelled":
        print("Cancellation failed!")
    
    # 6. Verify slot is back
    print("\n6. Verifying slot is available again...")
    docs_final = get_doctors("Cardiology")
    doc_final = next((d for d in docs_final["doctors"] if d["id"] == doctor["id"]), None)
    
    slot_restored = False
    for s in doc_final["available_slots"]:
        if s["date"] == slot["date"] and s["time"] == slot["time"]:
            slot_restored = True
            break
            
    if slot_restored:
         print("SUCCESS: Slot is available again.")
    else:
         print("ERROR: Slot was not restored!")

    # 7. Check Audit Log (Cancel)
    print("\n7. Checking Audit Log for CANCEL action...")
    logs = check_audit_log(appt_id)
    cancel_logs = [l for l in logs if l["action"] == "CANCEL"]
    if cancel_logs:
         print("SUCCESS: Found cancellation audit log.")
    else:
         print("ERROR: No cancellation audit log found.")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    main()
