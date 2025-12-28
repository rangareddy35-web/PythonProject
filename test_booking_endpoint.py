#!/usr/bin/env python
"""
Test script for booking appointment endpoint
This script tests the booking endpoint with sample data
"""

import requests
import json
import time
import sys

# Sample booking data - 5 different scenarios
BOOKING_DATA = {
    "basic": {
        "doctor_id": "doc001",
        "first_name": "John",
        "last_name": "Doe",
        "dob": "1990-05-15",
        "insurance_provider": "BlueCross",
        "reason": "Annual checkup",
        "requested_datetime": "2025-01-15T10:00:00"
    },
    "with_insurance": {
        "doctor_id": "doc002",
        "first_name": "Jane",
        "last_name": "Smith",
        "dob": "1985-08-22",
        "insurance_provider": "Aetna",
        "insurance_id": "AET123456789",
        "reason": "Cardiac consultation",
        "requested_datetime": "2025-01-20T14:30:00"
    },
    "emergency": {
        "doctor_id": "doc003",
        "first_name": "Robert",
        "last_name": "Johnson",
        "dob": "1978-03-10",
        "insurance_provider": "Medicare",
        "insurance_id": "MED987654321",
        "reason": "URGENT: Severe symptoms",
        "requested_datetime": "2025-01-15T11:00:00"
    },
    "routine": {
        "doctor_id": "doc004",
        "first_name": "Sarah",
        "last_name": "Williams",
        "dob": "1992-11-30",
        "insurance_provider": "United Healthcare",
        "reason": "Routine physical examination",
        "requested_datetime": "2025-01-22T09:00:00"
    },
    "specialist": {
        "doctor_id": "doc005",
        "first_name": "Michael",
        "last_name": "Brown",
        "dob": "1988-07-18",
        "insurance_provider": "Cigna",
        "insurance_id": "CIG456789012",
        "reason": "Dermatology consultation",
        "requested_datetime": "2025-01-25T15:30:00"
    }
}

BASE_URL = "http://localhost:8000/api/v1"

def test_health_check():
    """Test if API is running"""
    print("\n" + "="*70)
    print("TESTING HEALTH CHECK")
    print("="*70)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✓ Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {str(e)}")
        return False

def test_book_appointment(name, data):
    """Test booking appointment"""
    print("\n" + "="*70)
    print(f"TESTING BOOKING: {name.upper()}")
    print("="*70)
    print(f"\nRequest Data:")
    print(json.dumps(data, indent=2))
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/book-appointment",
            json=data,
            timeout=10
        )

        print(f"Status Code: {response.status_code}")
        print(f"\nResponse:")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 200:
            print("\n✓ BOOKING SUCCESSFUL!")
            return True
        else:
            print(f"\n✗ Booking failed with status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"✗ Connection failed - is the server running?")
        print(f"   Try: python main.py")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_list_appointments():
    """Test listing all appointments"""
    print("\n" + "="*70)
    print("LISTING ALL APPOINTMENTS")
    print("="*70)
    try:
        response = requests.get(f"{BASE_URL}/appointments", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"\nResponse:")
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "APPOINTMENT BOOKING ENDPOINT TEST" + " "*20 + "║")
    print("╚" + "="*68 + "╝")

    # Test health first
    if not test_health_check():
        print("\n" + "!"*70)
        print("SERVER NOT RUNNING")
        print("!"*70)
        print("\nPlease start the server with: python main.py")
        print("\nThen run this script again to test the booking endpoint")
        return

    # Test each booking scenario
    success_count = 0
    for name, data in BOOKING_DATA.items():
        if test_book_appointment(name, data):
            success_count += 1
        time.sleep(1)  # Small delay between requests

    # Try to list appointments
    test_list_appointments()

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Successful bookings: {success_count}/{len(BOOKING_DATA)}")

    if success_count == len(BOOKING_DATA):
        print("\n✓ ALL TESTS PASSED!")
    else:
        print(f"\n✗ {len(BOOKING_DATA) - success_count} booking(s) failed")

    print("\n" + "="*70)

if __name__ == "__main__":
    main()

