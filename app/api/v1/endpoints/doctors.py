from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.services.doctor_service import DoctorService
from app.schemas.schemas import Doctor as DoctorSchema

router = APIRouter()

@router.get("/doctors") #, response_model=List[DoctorSchema])
def get_doctors(db: Session = Depends(get_db)):
    """Get all doctors."""
    service = DoctorService(db)
    doctors = service.get_all_active_doctors()
    # Manual serialization again to match required output format if Schema differs
    return {
        "status": "success",
        "count": len(doctors),
        "doctors": [
            {
                "id": d.id,
                "name": d.name,
                "department": d.department,
                "specialization": d.specialization,
                "experience": d.experience,
                "available_slots": d.slots,
                "available_slots_count": len(d.slots)
            } for d in doctors
        ]
    }

@router.get("/available-slots")
def get_available_slots(department: Optional[str] = None, db: Session = Depends(get_db)):
    """Get available slots."""
    service = DoctorService(db)
    result_doctors = service.get_available_slots(department)

    return {
        "status": "success",
        "filter_department": department,
        "total_doctors": len(result_doctors),
        "doctors": result_doctors
    }
