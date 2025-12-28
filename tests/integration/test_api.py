"""
Comprehensive Testing Script for Appointment Booking API
Tests all endpoints and database functionality
"""
import requests
import json
import time
from datetime import datetime, date, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API Base URL
BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 10

class APITester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_data = {}

    def test_health_check(self):
        """Test health check endpoint"""
        logger.info("Testing health check...")
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=TIMEOUT)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            logger.info("✓ Health check passed")
            return True
        except Exception as e:
            logger.error(f"✗ Health check failed: {e}")
            return False

    def test_get_doctors(self):
        """Test get doctors endpoint"""
        logger.info("Testing get doctors...")
        try:
            response = self.session.get(f"{self.base_url}/doctors", timeout=TIMEOUT)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "doctors" in data
            logger.info(f"✓ Get doctors passed ({data['count']} doctors found)")

            if data["count"] > 0:
                self.test_data["doctor_id"] = data["doctors"][0]["id"]
            return True
        except Exception as e:
            logger.error(f"✗ Get doctors failed: {e}")
            return False

    def test_get_available_slots(self):
        """Test get available slots endpoint"""
        logger.info("Testing get available slots...")
        try:
            response = self.session.get(f"{self.base_url}/available-slots", timeout=TIMEOUT)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "doctors" in data
            logger.info(f"✓ Get available slots passed ({data['total_doctors']} doctors with slots)")

            if data["total_doctors"] > 0:
                doctor = data["doctors"][0]
                if doctor["available_slots"]:
                    slot = doctor["available_slots"][0]
                    self.test_data["slot_date"] = slot["date"]
                    self.test_data["slot_time"] = slot["time"]
                    self.test_data["slot_id"] = slot["id"]
                    self.test_data["doctor_id"] = doctor["id"]
            return True
        except Exception as e:
            logger.error(f"✗ Get available slots failed: {e}")
            return False

    def test_get_available_slots_by_department(self):
        """Test get available slots by department"""
        logger.info("Testing get available slots by department...")
        try:
            response = self.session.get(
                f"{self.base_url}/available-slots?department=Cardiology",
                timeout=TIMEOUT
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            logger.info(f"✓ Get available slots by department passed")
            return True
        except Exception as e:
            logger.error(f"✗ Get available slots by department failed: {e}")
            return False

    def test_create_patient(self):
        """Test create patient endpoint"""
        logger.info("Testing create patient...")
        try:
            payload = {
                "doctor_id": self.test_data.get("doctor_id", "doc001"),
                "first_name": "John",
                "last_name": "Doe",
                "dob": "1990-01-15",
                "insurance_provider": "BlueCross",
                "reason": "Routine Checkup",
                "requested_datetime": "2025-12-20T10:00:00"
            }

            response = self.session.post(
                f"{self.base_url}/patients",
                json=payload,
                timeout=TIMEOUT
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            self.test_data["patient_id"] = data.get("patient_id")
            logger.info("✓ Create patient passed")
            return True
        except Exception as e:
            logger.error(f"✗ Create patient failed: {e}")
            return False

    def test_book_appointment(self):
        """Test book appointment endpoint"""
        logger.info("Testing book appointment...")
        try:
            # Use tomorrow at 10:00 AM
            tomorrow = date.today() + timedelta(days=1)

            payload = {
                "doctor_id": self.test_data.get("doctor_id", "doc001"),
                "first_name": "Jane",
                "last_name": "Smith",
                "dob": "1985-05-20",
                "insurance_provider": "Aetna",
                "reason": "Annual Checkup",
                "requested_datetime": f"{tomorrow.isoformat()}T10:00:00"
            }

            response = self.session.post(
                f"{self.base_url}/book-appointment",
                json=payload,
                timeout=TIMEOUT
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "booked"
            self.test_data["appointment_id"] = data["appointment"].get("id")
            logger.info("✓ Book appointment passed")
            return True
        except Exception as e:
            logger.error(f"✗ Book appointment failed: {e}")
            return False

    def test_get_appointments(self):
        """Test get appointments endpoint"""
        logger.info("Testing get appointments...")
        try:
            response = self.session.get(
                f"{self.base_url}/appointments",
                timeout=TIMEOUT
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            logger.info(f"✓ Get appointments passed ({data['count']} appointments found)")
            return True
        except Exception as e:
            logger.error(f"✗ Get appointments failed: {e}")
            return False

    def test_get_appointment_details(self):
        """Test get specific appointment details"""
        logger.info("Testing get appointment details...")
        try:
            if not self.test_data.get("appointment_id"):
                logger.warning("⚠ Skipping: No appointment ID available")
                return True

            response = self.session.get(
                f"{self.base_url}/appointments/{self.test_data['appointment_id']}",
                timeout=TIMEOUT
            )
            assert response.status_code in [200, 404]
            logger.info("✓ Get appointment details passed")
            return True
        except Exception as e:
            logger.error(f"✗ Get appointment details failed: {e}")
            return False

    def test_cancel_appointment(self):
        """Test cancel appointment endpoint"""
        logger.info("Testing cancel appointment...")
        try:
            if not self.test_data.get("appointment_id"):
                logger.warning("⚠ Skipping: No appointment ID available")
                return True

            payload = {"appointment_id": self.test_data["appointment_id"]}

            response = self.session.post(
                f"{self.base_url}/cancel-appointment",
                json=payload,
                timeout=TIMEOUT
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "cancelled"
            logger.info("✓ Cancel appointment passed")
            return True
        except Exception as e:
            logger.error(f"✗ Cancel appointment failed: {e}")
            return False

    def test_get_audit_logs(self):
        """Test get audit logs endpoint"""
        logger.info("Testing get audit logs...")
        try:
            response = self.session.get(
                f"{self.base_url}/audit-logs",
                timeout=TIMEOUT
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            logger.info(f"✓ Get audit logs passed ({data['count']} logs found)")
            return True
        except Exception as e:
            logger.error(f"✗ Get audit logs failed: {e}")
            return False

    def test_get_audit_logs_by_action(self):
        """Test get audit logs by action"""
        logger.info("Testing get audit logs by action...")
        try:
            response = self.session.get(
                f"{self.base_url}/audit-logs?action=BOOK",
                timeout=TIMEOUT
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            logger.info(f"✓ Get audit logs by action passed")
            return True
        except Exception as e:
            logger.error(f"✗ Get audit logs by action failed: {e}")
            return False

    def run_all_tests(self):
        """Run all tests"""
        logger.info("=" * 70)
        logger.info("Starting Comprehensive API Tests")
        logger.info("=" * 70)

        tests = [
            self.test_health_check,
            self.test_get_doctors,
            self.test_get_available_slots,
            self.test_get_available_slots_by_department,
            self.test_create_patient,
            self.test_book_appointment,
            self.test_get_appointments,
            self.test_get_appointment_details,
            self.test_get_audit_logs,
            self.test_get_audit_logs_by_action,
            self.test_cancel_appointment,
        ]

        results = []
        for test_func in tests:
            try:
                result = test_func()
                results.append(result)
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                logger.error(f"Test {test_func.__name__} failed with exception: {e}")
                results.append(False)

        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("Test Summary")
        logger.info("=" * 70)
        passed = sum(results)
        total = len(results)
        logger.info(f"Passed: {passed}/{total}")

        if passed == total:
            logger.info("✓ All tests passed!")
        else:
            logger.warning(f"✗ {total - passed} test(s) failed")

        logger.info("=" * 70 + "\n")

        return passed == total


def main():
    """Main function"""
    import sys

    logger.info("Waiting for API to be ready...")

    # Wait for API to be ready
    tester = APITester()
    max_retries = 30
    for i in range(max_retries):
        try:
            if tester.test_health_check():
                logger.info("API is ready!")
                break
            time.sleep(1)
        except:
            if i < max_retries - 1:
                time.sleep(1)
            else:
                logger.error("API did not respond within timeout period")
                sys.exit(1)

    # Run tests
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

