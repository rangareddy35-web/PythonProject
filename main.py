from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
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
        data = payload.dict()
        required = ["first_name", "last_name", "dob", "insurance_provider", "reason", "requested_datetime"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            return {"status": "incomplete", "missing_fields": missing, "message": "Please provide the missing fields."}

        # All fields present: validate datetime and check availability
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
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        appts.append(appt)
        save_appointments(appts)
        logger.info(f"Appointment booked: {appt['id']}")

        return {"status": "booked", "appointment": appt}
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
