from typing import List, Optional
import logging
from .base import BaseRepository
from app.models.models import Doctor

logger = logging.getLogger(__name__)

class DoctorRepository(BaseRepository):
    """Repository for Doctor operations"""

    def create(self, doctor_id: str, name: str, department: str,
               specialization: str, experience: int, **kwargs) -> Doctor:
        """Create a new doctor"""
        doctor = Doctor(
            id=doctor_id,
            name=name,
            department=department,
            specialization=specialization,
            experience=experience,
            **kwargs
        )
        self.db.add(doctor)
        self.db.commit()
        self.db.refresh(doctor)
        logger.info(f"Doctor created: {doctor_id}")
        return doctor

    def get_by_id(self, doctor_id: str) -> Optional[Doctor]:
        """Get doctor by ID"""
        return self.db.query(Doctor).filter(Doctor.id == doctor_id).first()

    def get_by_department(self, department: str) -> List[Doctor]:
        """Get all doctors in a department"""
        return self.db.query(Doctor).filter(
            Doctor.department == department,
            Doctor.is_active == True
        ).all()

    def get_all_active(self) -> List[Doctor]:
        """Get all active doctors"""
        return self.db.query(Doctor).filter(Doctor.is_active == True).all()
