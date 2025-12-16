from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime, timezone
import json
import os
import uuid
import logging

# Configure logging for deployment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Appointment Booking API", version="1.0.0")

# Use environment variable for file path to support different deployment environments
APPOINTMENTS_FILE = os.getenv("APPOINTMENTS_FILE", "appointments.json")
DOCTORS_SLOTS_FILE = os.getenv("DOCTORS_SLOTS_FILE", "doctors_slots.json")

# Helper functions to persist appointments simply in a JSON file
def load_appointments() -> List[dict]:
    if not os.path.exists(APPOINTMENTS_FILE):
        return []
    try:
        with open(APPOINTMENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_appointments(appts: List[dict]):
    with open(APPOINTMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(appts, f, indent=2)

def load_doctors_slots() -> dict:
    """Load doctors and available slots from JSON file."""
    if not os.path.exists(DOCTORS_SLOTS_FILE):
        return {"doctors": []}
    try:
        with open(DOCTORS_SLOTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        logger.error(f"Error loading doctors slots from {DOCTORS_SLOTS_FILE}")
        return {"doctors": []}

class AppointmentRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[str] = None  # expect YYYY-MM-DD
    insurance_provider: Optional[str] = None
    reason: Optional[str] = None
    requested_datetime: Optional[str] = None  # expect full ISO 8601 datetime

    @field_validator("dob")
    @classmethod
    def validate_dob(cls, v):
        if v is None:
            return v
        try:
            # accept date in YYYY-MM-DD format
            datetime.fromisoformat(v)
            return v
        except Exception:
            raise ValueError("dob must be in ISO format YYYY-MM-DD")

    @field_validator("requested_datetime")
    @classmethod
    def validate_requested_datetime(cls, v):
        if v is None:
            return v
        try:
            # accept full ISO datetime
            datetime.fromisoformat(v)
            return v
        except Exception:
            raise ValueError("requested_datetime must be a valid ISO 8601 datetime string")

@app.post("/book-appointment")
def book_appointment(payload: AppointmentRequest):
    """Endpoint that collects appointment fields. If some required fields are missing, returns which fields to ask for next.
    Required fields: first_name, last_name, dob, insurance_provider, reason, requested_datetime
    When all are present, checks availability and books if free."""
    try:
        data = payload.model_dump()
        logger.info("Received booking request from Retell Payload=%s", data)
        # All fields are now guaranteed to be present due to Pydantic validation
        # Validate datetime and check availability
        try:
            req_dt = datetime.fromisoformat(data["requested_datetime"])
        except Exception:
            logger.error(f"Invalid datetime format in booking: {data['requested_datetime']}")
            raise HTTPException(status_code=400, detail="requested_datetime must be a valid ISO 8601 datetime string")

        appts = load_appointments()
        for a in appts:
            if a.get("requested_datetime") == req_dt.isoformat():
                return {"status": "unavailable", "message": "Requested time is already booked. Please provide a new booking time."}

        # Book the appointment
        appt = {
            "id": str(uuid.uuid4()),
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "dob": data["dob"],
            "insurance_provider": data["insurance_provider"],
            "reason": data["reason"],
            "requested_datetime": req_dt.isoformat(),
            "created_at": datetime.now().isoformat() + "Z"
        }
        appts.append(appt)
        save_appointments(appts)
        logger.info(f"Appointment booked: {appt['id']}")

        return {"status": "booked", "appointment": appt}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error booking appointment: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/appointments")
def get_all_appointments():
    """Retrieve all booked appointments."""
    try:
        appts = load_appointments()
        return {"status": "success", "total": len(appts), "appointments": appts}
    except Exception as e:
        logger.error(f"Error retrieving appointments: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/available-slots")
def get_available_slots(department: Optional[str] = None):
    """
    Endpoint that provides available slots for doctors across various departments.

    Query Parameters:
    - department (optional): Filter by specific department (e.g., 'Cardiology', 'Neurology')

    Returns:
    - List of doctors with their available time slots
    - Only slots with status 'available' are returned
    """
    try:
        logger.info(f"Fetching available slots. Filter by department: {department}")

        doctors_data = load_doctors_slots()
        doctors = doctors_data.get("doctors", [])

        # Filter by department if provided
        if department:
            doctors = [doc for doc in doctors if doc.get("department", "").lower() == department.lower()]
            if not doctors:
                return {
                    "status": "not_found",
                    "message": f"No doctors found in {department} department",
                    "doctors": []
                }

        # Process doctors and filter only available slots
        result_doctors = []
        for doctor in doctors:
            available_slots = [
                slot for slot in doctor.get("available_slots", [])
                if slot.get("status") == "available"
            ]

            if available_slots:  # Only include doctors with available slots
                result_doctors.append({
                    "id": doctor.get("id"),
                    "name": doctor.get("name"),
                    "department": doctor.get("department"),
                    "specialization": doctor.get("specialization"),
                    "experience": doctor.get("experience"),
                    "available_slots": available_slots,
                    "available_slots_count": len(available_slots)
                })

        return {
            "status": "success",
            "filter_department": department,
            "total_doctors": len(result_doctors),
            "doctors": result_doctors
        }

    except Exception as e:
        logger.error(f"Error fetching available slots: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

