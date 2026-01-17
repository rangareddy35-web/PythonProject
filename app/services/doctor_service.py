from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories.doctor import DoctorRepository
from app.schemas.schemas import Doctor as DoctorSchema

class DoctorService:
    def __init__(self, db: Session):
        self.db = db
        self.doctor_repo = DoctorRepository(db)

    def get_all_active_doctors(self, include_slots: bool = False, slot_limit: int = 5, specialization: Optional[str] = None) -> List[dict]:
        """Get all active doctors with optional available slots and specialization filtering"""
        doctors = self.doctor_repo.get_all_active(specialization=specialization)
        result = []
        for doc in doctors:
            doc_data = self._format_doctor(doc, include_slots, slot_limit)
            result.append(doc_data)
        return result

    def get_doctor_by_id(self, doctor_id: str, include_slots: bool = True, slot_limit: int = 20) -> Optional[dict]:
        """Get a single doctor by ID with slots"""
        doc = self.doctor_repo.get_by_id(doctor_id)
        if not doc:
            return None
        return self._format_doctor(doc, include_slots, slot_limit)

    def _format_doctor(self, doc, include_slots: bool, slot_limit: int) -> dict:
        """Helper to format doctor data"""
        from datetime import date
        today = date.today()
        
        doc_data = {
            "id": doc.id,
            "name": doc.name,
            "department": doc.department,
            "specialization": doc.specialization,
            "experience": doc.experience,
        }
        
        # Filter (available + today/future) and sort by date and time
        avail_slots = [
            s for s in doc.slots 
            if s.status == "available" and s.date >= today
        ]
        avail_slots.sort(key=lambda x: (x.date, x.time))
        
        doc_data["available_slots_count"] = len(avail_slots)
        
        if include_slots:
            doc_data["available_slots"] = avail_slots[:slot_limit]
        
        return doc_data

    def get_available_slots(self, department: Optional[str] = None, slot_limit: int = 10):
        """Get available slots logic with limiting"""
        from datetime import date
        today = date.today()
        
        if department:
            doctors = self.doctor_repo.get_by_department(department)
        else:
            doctors = self.doctor_repo.get_all_active()
        
        result_doctors = []
        for doc in doctors:
            # Filter (available + today/future) and sort by date and time
            avail_slots = [
                s for s in doc.slots 
                if s.status == "available" and s.date >= today
            ]
            avail_slots.sort(key=lambda x: (x.date, x.time))
            
            if avail_slots:
                result_doctors.append({
                    "id": doc.id,
                    "name": doc.name,
                    "department": doc.department,
                    "specialization": doc.specialization,
                    "experience": doc.experience,
                    "available_slots": avail_slots[:slot_limit],
                    "available_slots_count": len(avail_slots)
                })
        return result_doctors
