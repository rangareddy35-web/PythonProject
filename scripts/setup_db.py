"""
Setup script for PostgreSQL Appointment Booking System
Initialize database, create sample data, etc.
"""
import os
import logging
from datetime import date, time, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import database and models
# Import database and models
from app.db.session import engine, SessionLocal
from app.models.models import Department, Doctor, AvailableSlot, SlotStatus
from app.repositories.doctor import DoctorRepository
from app.repositories.available_slot import AvailableSlotRepository

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ranga:lQHuZjjAtYduMoYuAL6FSHTsBd75u3Qd@dpg-d58jgkogjchc73a744k0-a.virginia-postgres.render.com/ai_receptionist_3gp5")


def setup_database():
    """Initialize database schema"""
    logger.info("Setting up database...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database schema created successfully")
    except Exception as e:
        logger.error(f"✗ Failed to setup database: {e}")
        raise


def create_departments(db):
    """Create initial departments"""
    logger.info("Creating departments...")
    departments_data = [
        ("cardiology", "Cardiology - Heart & Cardiovascular"),
        ("neurology", "Neurology - Neurological Disorders"),
        ("orthopedics", "Orthopedics - Bone & Joint Surgery"),
        ("pediatrics", "Pediatrics - Child Healthcare"),
        ("dermatology", "Dermatology - Skin Disorders"),
    ]

    for dept_id, dept_name in departments_data:
        existing = db.query(Department).filter(Department.id == dept_id).first()
        if not existing:
            dept = Department(id=dept_id, name=dept_name)
            db.add(dept)
            logger.info(f"  - Created department: {dept_name}")

    db.commit()
    logger.info("✓ Departments created")


def create_doctors(db):
    """Create sample doctors"""
    logger.info("Creating sample doctors...")
    doctors_data = [
        {
            "id": "doc001",
            "name": "Dr. Sarah Johnson",
            "department": "Cardiology",
            "specialization": "Heart & Cardiovascular",
            "experience": 12,
            "email": "sarah.johnson@hospital.com",
            "phone": "+1-555-0001"
        },
        {
            "id": "doc002",
            "name": "Dr. Rajesh Kumar",
            "department": "Neurology",
            "specialization": "Neurological Disorders",
            "experience": 15,
            "email": "rajesh.kumar@hospital.com",
            "phone": "+1-555-0002"
        },
        {
            "id": "doc003",
            "name": "Dr. Emily White",
            "department": "Orthopedics",
            "specialization": "Bone & Joint Surgery",
            "experience": 10,
            "email": "emily.white@hospital.com",
            "phone": "+1-555-0003"
        },
        {
            "id": "doc004",
            "name": "Dr. Michael Chen",
            "department": "Pediatrics",
            "specialization": "Child Healthcare",
            "experience": 8,
            "email": "michael.chen@hospital.com",
            "phone": "+1-555-0004"
        },
        {
            "id": "doc005",
            "name": "Dr. Lisa Anderson",
            "department": "Dermatology",
            "specialization": "Skin Disorders",
            "experience": 11,
            "email": "lisa.anderson@hospital.com",
            "phone": "+1-555-0005"
        }
    ]

    for doc_data in doctors_data:
        existing = db.query(Doctor).filter(Doctor.id == doc_data["id"]).first()
        if not existing:
            repo = DoctorRepository(db)
            repo.create(**doc_data)
            logger.info(f"  - Created doctor: {doc_data['name']}")

    logger.info("✓ Doctors created")


def create_available_slots(db):
    """Create sample available slots for doctors"""
    logger.info("Creating available slots...")
    
    slot_repo = AvailableSlotRepository(db)

    doctor_ids = ["doc001", "doc002", "doc003", "doc004", "doc005"]
    base_date = date.today()

    # Create slots for next 30 days
    for day_offset in range(30):
        slot_date = base_date + timedelta(days=day_offset)

        # Skip weekends
        if slot_date.weekday() >= 5:
            continue

        for doctor_id in doctor_ids:
            # Morning slots
            for hour, minute in [(9, 0), (9, 30), (10, 0), (10, 30), (11, 0), (11, 30)]:
                slot_time = time(hour=hour, minute=minute)
                existing = db.query(AvailableSlot).filter(
                    AvailableSlot.doctor_id == doctor_id,
                    AvailableSlot.date == slot_date,
                    AvailableSlot.time == slot_time
                ).first()
                if not existing:
                    slot_repo.create(
                        doctor_id, slot_date, slot_time, 30
                    )

            # Afternoon slots
            for hour, minute in [(14, 0), (14, 30), (15, 0), (15, 30), (16, 0), (16, 30)]:
                slot_time = time(hour=hour, minute=minute)
                existing = db.query(AvailableSlot).filter(
                    AvailableSlot.doctor_id == doctor_id,
                    AvailableSlot.date == slot_date,
                    AvailableSlot.time == slot_time
                ).first()
                if not existing:
                    slot_repo.create(
                        doctor_id, slot_date, slot_time, 30
                    )

    logger.info("✓ Available slots created")


def verify_setup(db):
    """Verify database setup"""
    logger.info("\nVerifying database setup...")

    doctor_count = db.query(Doctor).count()
    slot_count = db.query(AvailableSlot).count()
    dept_count = db.query(Department).count()

    logger.info(f"  - Departments: {dept_count}")
    logger.info(f"  - Doctors: {doctor_count}")
    logger.info(f"  - Available slots: {slot_count}")

    if doctor_count > 0 and slot_count > 0:
        logger.info("✓ Database setup verified successfully!")
        return True
    else:
        logger.warning("✗ Some data might be missing")
        return False


def main():
    """Main setup function"""
    logger.info("=" * 60)
    logger.info("PostgreSQL Appointment Booking System - Setup")
    logger.info("=" * 60)
    logger.info(f"Database URL: {DATABASE_URL}\n")

    try:
        # Setup database schema
        setup_database()

        # Create session
        db = SessionLocal()

        try:
            # Create departments
            create_departments(db)

            # Create doctors
            create_doctors(db)

            # Create available slots
            create_available_slots(db)

            # Verify setup
            verify_setup(db)

            logger.info("\n" + "=" * 60)
            logger.info("✓ Setup completed successfully!")
            logger.info("=" * 60)
            logger.info("\nYou can now start the API:")
            logger.info("  python -m uvicorn main_pg:app --reload")
            logger.info("=" * 60 + "\n")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"\n✗ Setup failed: {e}")
        raise


if __name__ == "__main__":
    main()

