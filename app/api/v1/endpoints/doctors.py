from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.services.doctor_service import DoctorService
from app.schemas.schemas import Doctor as DoctorSchema

router = APIRouter()

@router.get("/doctors") #, response_model=List[DoctorSchema])
def get_doctors(
    include_slots: bool = False,
    slot_limit: int = 5,
    specialization: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all doctors with optional slot inclusion and specialization filtering."""
    service = DoctorService(db)
    doctors_data = service.get_all_active_doctors(
        include_slots=include_slots, 
        slot_limit=slot_limit,
        specialization=specialization
    )
    return {
        "status": "success",
        "count": len(doctors_data),
        "doctors": doctors_data
    }

@router.get("/doctors/{doctor_id}")
def get_doctor(
    doctor_id: str,
    include_slots: bool = True,
    slot_limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get specific doctor details and available slots."""
    service = DoctorService(db)
    doctor = service.get_doctor_by_id(doctor_id, include_slots=include_slots, slot_limit=slot_limit)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return {
        "status": "success",
        "doctor": doctor
    }

@router.get("/available-slots")
def get_available_slots(
    department: Optional[str] = None,
    slot_limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get available slots by department."""
    service = DoctorService(db)
    result_doctors = service.get_available_slots(department, slot_limit=slot_limit)

    return {
        "status": "success",
        "filter_department": department,
        "total_doctors": len(result_doctors),
        "doctors": result_doctors
    }
