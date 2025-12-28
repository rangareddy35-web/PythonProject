from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.services.appointment_service import AppointmentService
from app.schemas.schemas import AppointmentRequest
import uuid

router = APIRouter()

@router.post("/book-appointment")
def book_appointment(payload: AppointmentRequest, db: Session = Depends(get_db)):
    """Book an appointment."""
    service = AppointmentService(db)
    result = service.book_appointment(payload)
    return {"status": "booked", "appointment": result}

@router.get("/appointments")
def get_all_appointments(db: Session = Depends(get_db)):
    service = AppointmentService(db)
    appts = service.get_all_appointments()
    return {"status": "success", "appointments": appts, "count": len(appts)}

@router.post("/cancel-appointment")
def cancel_appointment(appointment_id: str = Body(..., embed=True), db: Session = Depends(get_db)):
    service = AppointmentService(db)
    return service.cancel_appointment(appointment_id)

@router.get("/appointments/{appointment_id}")
def get_appointment(appointment_id: str, db: Session = Depends(get_db)):
    """Get appointment by ID"""
    try:
        appt_uuid = uuid.UUID(appointment_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    service = AppointmentService(db)
    try:
        appt = service.get_by_id(appt_uuid)
        return {"status": "success", "appointment": appt}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
