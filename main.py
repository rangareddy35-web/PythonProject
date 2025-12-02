from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
import json
import os
import uuid

app = FastAPI()

APPOINTMENTS_FILE = "appointments.json"

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

    @validator("dob")
    def validate_dob(cls, v):
        if v is None:
            return v
        try:
            # accept date in YYYY-MM-DD format
            datetime.fromisoformat(v)
            return v
        except Exception:
            raise ValueError("dob must be in ISO format YYYY-MM-DD")

    @validator("requested_datetime")
    def validate_requested_datetime(cls, v):
        if v is None:
            return v
        try:
            # accept full ISO datetime
            datetime.fromisoformat(v)
            return v
        except Exception:
            raise ValueError("requested_datetime must be a valid ISO 8601 datetime string")

@app.get("/")
def home():
    return {"message": "API is live!"}

@app.post("/test")
def test(data: dict):
    return {"received": data}

@app.post("/retell-webhook")
async def retell_webhook(request: Request):
    data = await request.json()
    print("Received from Retell:", data)
    return {"status": "received"}

@app.get("/availability")
def check_availability(requested_datetime: str):
    """Check whether the exact requested_datetime slot is free. Expects ISO 8601 datetime string."""
    try:
        req_dt = datetime.fromisoformat(requested_datetime)
    except Exception:
        raise HTTPException(status_code=400, detail="requested_datetime must be a valid ISO 8601 datetime")

    appts = load_appointments()
    for a in appts:
        if a.get("requested_datetime") == req_dt.isoformat():
            return {"available": False, "reason": "Slot already booked"}
    return {"available": True}

@app.post("/book-appointment")
def book_appointment(payload: AppointmentRequest):
    """Endpoint that collects appointment fields. If some required fields are missing, returns which fields to ask for next.
    Required fields: first_name, last_name, dob, insurance_provider, reason, requested_datetime
    When all are present, checks availability and books if free."""
    data = payload.dict()
    required = ["first_name", "last_name", "dob", "insurance_provider", "reason", "requested_datetime"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return {"status": "incomplete", "missing_fields": missing, "message": "Please provide the missing fields."}

    # All fields present: validate datetime and check availability
    try:
        req_dt = datetime.fromisoformat(data["requested_datetime"])
    except Exception:
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

    return {"status": "booked", "appointment": appt}
