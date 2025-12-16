# API Documentation - Available Slots Endpoint

## Overview
The **Available Slots** endpoint provides real-time information about doctors and their available appointment slots across various departments. This endpoint allows clients to query available slots with optional filtering by department.

## Endpoint Details

### GET /available-slots

**Purpose:** Retrieve available appointment slots for doctors in various departments.

**Base URL:** `http://localhost:8000`

**Full URL:** `http://localhost:8000/available-slots`

---

## Query Parameters

### `department` (Optional)
- **Type:** String
- **Description:** Filter results by doctor's department
- **Case-Insensitive:** Yes
- **Valid Values:** 
  - `Cardiology`
  - `Neurology`
  - `Orthopedics`
  - `Dermatology`
  - `General Medicine`
  - `Pediatrics`

**Example:**
```
GET /available-slots?department=Cardiology
```

---

## Request Examples

### 1. Get All Available Slots
```bash
curl -X GET "http://localhost:8000/available-slots"
```

### 2. Get Slots by Department
```bash
curl -X GET "http://localhost:8000/available-slots?department=Cardiology"
```

### 3. Using Python requests library
```python
import requests

# Get all available slots
response = requests.get("http://localhost:8000/available-slots")
data = response.json()

# Get slots for specific department
response = requests.get("http://localhost:8000/available-slots", 
                       params={"department": "Pediatrics"})
data = response.json()
```

---

## Response Structure

### Success Response (HTTP 200)

```json
{
  "status": "success",
  "filter_department": null,
  "total_doctors": 6,
  "doctors": [
    {
      "id": "doc001",
      "name": "Dr. Sarah Johnson",
      "department": "Cardiology",
      "specialization": "Heart & Cardiovascular",
      "experience": 12,
      "available_slots_count": 4,
      "available_slots": [
        {
          "date": "2025-12-18",
          "time": "09:00",
          "duration_minutes": 30,
          "status": "available"
        },
        {
          "date": "2025-12-18",
          "time": "09:30",
          "duration_minutes": 30,
          "status": "available"
        },
        {
          "date": "2025-12-19",
          "time": "14:00",
          "duration_minutes": 30,
          "status": "available"
        }
      ]
    }
  ]
}
```

### Response Fields

**Root Level:**
- `status` (string): API response status ("success" or "not_found")
- `filter_department` (string | null): Applied department filter (null if no filter)
- `total_doctors` (integer): Number of doctors returned
- `doctors` (array): List of doctor objects

**Doctor Object:**
- `id` (string): Unique identifier for the doctor
- `name` (string): Full name of the doctor
- `department` (string): Medical department
- `specialization` (string): Doctor's area of specialization
- `experience` (integer): Years of experience
- `available_slots_count` (integer): Total number of available slots
- `available_slots` (array): List of available time slots

**Slot Object:**
- `date` (string): Date in YYYY-MM-DD format
- `time` (string): Time in HH:MM format (24-hour)
- `duration_minutes` (integer): Duration of the appointment in minutes
- `status` (string): Slot status ("available" or "booked")

---

## Error Responses

### Department Not Found (HTTP 200)
```json
{
  "status": "not_found",
  "message": "No doctors found in InvalidDept department",
  "doctors": []
}
```

### Internal Server Error (HTTP 500)
```json
{
  "detail": "Internal server error"
}
```

---

## Sample Data

The endpoint uses sample data from `doctors_slots.json` containing:

### Available Doctors

| ID | Name | Department | Specialization | Experience |
|----|------|-----------|----------------|------------|
| doc001 | Dr. Sarah Johnson | Cardiology | Heart & Cardiovascular | 12 years |
| doc002 | Dr. Rajesh Kumar | Neurology | Neurological Disorders | 15 years |
| doc003 | Dr. Emily White | Orthopedics | Bone & Joint Surgery | 10 years |
| doc004 | Dr. Priya Singh | Dermatology | Skin Diseases & Cosmetic Surgery | 8 years |
| doc005 | Dr. Michael Chen | General Medicine | Internal Medicine & Preventive Care | 18 years |
| doc006 | Dr. Lisa Anderson | Pediatrics | Child Health & Development | 11 years |

### Sample Available Slots
- **Dates:** December 18-20, 2025
- **Time Slots:** Multiple slots throughout the day (09:00 - 15:30)
- **Duration:** 30 minutes per slot
- **Status:** Mix of available and booked slots

---

## Usage Scenarios

### Scenario 1: Find any doctor with available slots
```bash
GET /available-slots
```
Returns all doctors across all departments who have available slots.

### Scenario 2: Find a cardiologist
```bash
GET /available-slots?department=Cardiology
```
Returns cardiologists with available appointment slots.

### Scenario 3: Find pediatricians
```bash
GET /available-slots?department=Pediatrics
```
Returns pediatricians with available appointment slots.

---

## Integration Example

### Using JavaScript/Fetch API
```javascript
// Fetch all available slots
fetch('http://localhost:8000/available-slots')
  .then(response => response.json())
  .then(data => {
    console.log('Available Doctors:', data.doctors);
    data.doctors.forEach(doctor => {
      console.log(`${doctor.name} - ${doctor.department}`);
      console.log(`Available Slots: ${doctor.available_slots_count}`);
    });
  });

// Fetch slots for specific department
fetch('http://localhost:8000/available-slots?department=Cardiology')
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      data.doctors.forEach(doctor => {
        console.log(`${doctor.name}: ${doctor.available_slots_count} slots`);
      });
    }
  });
```

---

## Running the Application

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

### 3. Access API Documentation
FastAPI automatically provides interactive documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 4. Run Tests
```bash
python test_available_slots.py
```

---

## Notes

- Only slots with status "available" are returned by this endpoint
- Booked slots are filtered out automatically
- Department filtering is case-insensitive
- Response data comes from the `doctors_slots.json` file
- All times are in 24-hour format (HH:MM)
- All dates follow YYYY-MM-DD format

---

## Support

For issues or questions about this endpoint, please refer to the main README.md file or contact the development team.

