from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories.patient import PatientRepository
from app.schemas.schemas import Patient as PatientSchema
import uuid

class PatientService:
    def __init__(self, db: Session):
        self.db = db
        self.patient_repo = PatientRepository(db)

    def create_patient(self, patient_data: PatientSchema):
        """Create a new patient"""
        return self.patient_repo.create(
            first_name=patient_data.first_name,
            last_name=patient_data.last_name,
            dob=patient_data.dob,
            insurance_provider=patient_data.insurance_provider
        )

    def get_patient(self, patient_id: uuid.UUID):
        return self.patient_repo.get_by_id(patient_id)
