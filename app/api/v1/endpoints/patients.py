from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.schemas import Patient as PatientSchema
from app.services.patient_service import PatientService

router = APIRouter()

@router.post("/patients", response_model=PatientSchema)
def create_patient(patient: PatientSchema, db: Session = Depends(get_db)):
    """Create a new patient."""
    service = PatientService(db)
    return service.create_patient(patient)
