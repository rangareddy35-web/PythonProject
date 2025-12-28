from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories.doctor import DoctorRepository
from app.schemas.schemas import Doctor as DoctorSchema

class DoctorService:
    def __init__(self, db: Session):
        self.db = db
        self.doctor_repo = DoctorRepository(db)

    def get_all_active_doctors(self) -> List[DoctorSchema]:
        """Get all active doctors with their available slots"""
        return self.doctor_repo.get_all_active()

    def get_available_slots(self, department: Optional[str] = None):
        """Get available slots logic"""
        if department:
            doctors = self.doctor_repo.get_by_department(department)
        else:
            doctors = self.doctor_repo.get_all_active()
        
        result_doctors = []
        for doc in doctors:
            avail_slots = [s for s in doc.slots if s.status == "available"]
            if avail_slots:
                result_doctors.append({
                    "id": doc.id,
                    "name": doc.name,
                    "department": doc.department,
                    "specialization": doc.specialization,
                    "experience": doc.experience,
                    "available_slots": avail_slots,
                    "available_slots_count": len(avail_slots)
                })
        return result_doctors
