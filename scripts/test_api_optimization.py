from app.db.session import SessionLocal
from app.services.doctor_service import DoctorService
import json

def test_optimization():
    db = SessionLocal()
    try:
        service = DoctorService(db)
        
        print("--- Testing default (no slots) ---")
        doctors_no_slots = service.get_all_active_doctors(include_slots=False)
        print(f"Count: {len(doctors_no_slots)}")
        if doctors_no_slots:
            print(f"First doctor slots key present: {'available_slots' in doctors_no_slots[0]}")
            print(f"First doctor slots count: {doctors_no_slots[0].get('available_slots_count')}")

        print("\n--- Testing specialization='Cardiology' ---")
        doctors_cardio = service.get_all_active_doctors(specialization="Cardiology")
        print(f"Cardio doctors: {len(doctors_cardio)}")
        if doctors_cardio:
            print(f"Doctor specialization: {doctors_cardio[0].get('specialization')}")

        print("\n--- Testing get_doctor_by_id ('DOC001') ---")
        doctor = service.get_doctor_by_id("DOC001", include_slots=True, slot_limit=3)
        if doctor:
            print(f"Doctor name: {doctor.get('name')}")
            print(f"Slots returned: {len(doctor.get('available_slots', []))}")
            print(f"Total available slots count: {doctor.get('available_slots_count')}")
        else:
            print("Doctor 'DOC001' not found!")

    finally:
        db.close()

if __name__ == "__main__":
    test_optimization()
