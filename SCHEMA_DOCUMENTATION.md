# Available Slots Response Schema Documentation

## Overview

This document provides a comprehensive guide to the response schema for the `GET /available-slots` endpoint. The schema is defined in JSON Schema Draft 7 format and validates all possible responses from the endpoint.

---

## Table of Contents

1. [Response Types](#response-types)
2. [Success Response](#success-response)
3. [Not Found Response](#not-found-response)
4. [Error Response](#error-response)
5. [Object Definitions](#object-definitions)
6. [Data Constraints](#data-constraints)
7. [Examples](#examples)

---

## Response Types

The `/available-slots` endpoint can return three different response types:

### 1. Success Response (HTTP 200)
Returns doctors with available slots matching the query criteria.

### 2. Not Found Response (HTTP 200)
Returns when department filter is applied but no doctors are found.

### 3. Error Response (HTTP 500)
Returns when a server error occurs.

---

## Success Response

### Structure
```json
{
  "status": "success",
  "filter_department": null | "string",
  "total_doctors": integer,
  "doctors": [Doctor]
}
```

### Field Definitions

#### `status` (required, string)
- **Type:** Enum
- **Valid Values:** `"success"`
- **Description:** Indicates successful retrieval of doctor and slot data
- **Example:** `"success"`

#### `filter_department` (required, string | null)
- **Type:** String or Null
- **Valid Values:** 
  - `null` - No department filter applied
  - `"Cardiology"` - Cardiology department
  - `"Neurology"` - Neurology department
  - `"Orthopedics"` - Orthopedics department
  - `"Dermatology"` - Dermatology department
  - `"General Medicine"` - General Medicine department
  - `"Pediatrics"` - Pediatrics department
- **Description:** Indicates which department filter (if any) was applied to the results
- **Example:** `null` or `"Cardiology"`

#### `total_doctors` (required, integer)
- **Type:** Integer
- **Minimum:** 0
- **Description:** Total count of doctors returned in the response
- **Example:** `6` or `1`

#### `doctors` (required, array)
- **Type:** Array of Doctor objects
- **Minimum Items:** 0
- **Maximum Items:** Unlimited
- **Description:** List of doctors with available appointment slots
- **Example:** Array of 1-6 Doctor objects

---

## Doctor Object

### Structure
```json
{
  "id": "string",
  "name": "string",
  "department": "string",
  "specialization": "string",
  "experience": integer,
  "available_slots_count": integer,
  "available_slots": [AvailableSlot]
}
```

### Field Definitions

#### `id` (required, string)
- **Type:** String
- **Pattern:** `^doc[0-9]{3}$`
- **Description:** Unique identifier for the doctor
- **Format:** "doc" followed by 3 digits
- **Examples:** `"doc001"`, `"doc002"`, `"doc003"`

#### `name` (required, string)
- **Type:** String
- **Minimum Length:** 2 characters
- **Maximum Length:** 100 characters
- **Description:** Full name of the doctor
- **Format:** Title + First Name + Last Name (e.g., "Dr. FirstName LastName")
- **Examples:** `"Dr. Sarah Johnson"`, `"Dr. Rajesh Kumar"`

#### `department` (required, string)
- **Type:** Enum string
- **Valid Values:**
  - `"Cardiology"` - Heart and cardiovascular medicine
  - `"Neurology"` - Nervous system and brain disorders
  - `"Orthopedics"` - Bones and joints
  - `"Dermatology"` - Skin and skin conditions
  - `"General Medicine"` - Internal medicine and preventive care
  - `"Pediatrics"` - Child health and development
- **Description:** Medical department the doctor specializes in
- **Example:** `"Cardiology"`

#### `specialization` (required, string)
- **Type:** String
- **Minimum Length:** 5 characters
- **Maximum Length:** 150 characters
- **Description:** Doctor's specific area of specialization within their department
- **Examples:**
  - `"Heart & Cardiovascular"`
  - `"Neurological Disorders"`
  - `"Bone & Joint Surgery"`

#### `experience` (required, integer)
- **Type:** Integer
- **Minimum:** 0 years
- **Maximum:** 60 years
- **Description:** Number of years of medical practice experience
- **Examples:** `8`, `12`, `15`, `18`

#### `available_slots_count` (required, integer)
- **Type:** Integer
- **Minimum:** 0
- **Description:** Total number of available appointment slots for this doctor
- **Notes:** Automatically calculated from available_slots array length
- **Examples:** `0`, `4`, `5`

#### `available_slots` (required, array)
- **Type:** Array of AvailableSlot objects
- **Minimum Items:** 0
- **Description:** List of available appointment time slots
- **Notes:** Only slots with status "available" are included (booked slots are filtered out)
- **Example:** Array of 0-6 AvailableSlot objects

---

## Available Slot Object

### Structure
```json
{
  "date": "string",
  "time": "string",
  "duration_minutes": integer,
  "status": "string"
}
```

### Field Definitions

#### `date` (required, string)
- **Type:** String (Date format)
- **Format:** ISO 8601 date format `YYYY-MM-DD`
- **Description:** The appointment date
- **Examples:** `"2025-12-18"`, `"2025-12-19"`, `"2025-12-20"`

#### `time` (required, string)
- **Type:** String (Time format)
- **Format:** 24-hour time format `HH:MM`
- **Pattern:** `^([01]?[0-9]|2[0-3]):[0-5][0-9]$`
- **Valid Range:** 00:00 to 23:59
- **Description:** The appointment time in 24-hour format
- **Examples:** `"09:00"`, `"14:30"`, `"15:45"`

#### `duration_minutes` (required, integer)
- **Type:** Integer
- **Minimum:** 15 minutes
- **Maximum:** 480 minutes (8 hours)
- **Description:** Duration of the appointment slot in minutes
- **Common Values:** `15`, `30`, `45`, `60`
- **Examples:** `30`, `45`

#### `status` (required, string)
- **Type:** Enum string
- **Valid Values:**
  - `"available"` - Slot is available for booking
  - `"booked"` - Slot is already booked (typically filtered out)
- **Description:** Current availability status of the slot
- **Note:** Endpoint only returns slots with "available" status
- **Example:** `"available"`

---

## Not Found Response

### Structure
```json
{
  "status": "not_found",
  "message": "string",
  "doctors": []
}
```

### When This Occurs
- Department filter is provided
- No doctors exist in the specified department

### Field Definitions

#### `status` (required, string)
- **Valid Values:** `"not_found"`
- **Description:** Indicates no doctors were found

#### `message` (required, string)
- **Description:** Human-readable error message
- **Format:** `"No doctors found in {department} department"`
- **Example:** `"No doctors found in Surgery department"`

#### `doctors` (required, array)
- **Type:** Empty array
- **Description:** Empty array indicating no results
- **Value:** `[]`

---

## Error Response

### Structure
```json
{
  "detail": "string"
}
```

### When This Occurs
- Internal server error (HTTP 500)
- Unexpected exception during processing

### Field Definitions

#### `detail` (required, string)
- **Description:** Error message describing what went wrong
- **Example:** `"Internal server error"`

---

## Object Definitions

### AvailableSlot Definition
```typescript
interface AvailableSlot {
  date: string;              // YYYY-MM-DD format
  time: string;              // HH:MM format (24-hour)
  duration_minutes: number;  // 15-480 minutes
  status: "available" | "booked";
}
```

### Doctor Definition
```typescript
interface Doctor {
  id: string;                      // Pattern: doc[0-9]{3}
  name: string;                    // 2-100 characters
  department: DepartmentType;      // One of 6 departments
  specialization: string;          // 5-150 characters
  experience: number;              // 0-60 years
  available_slots_count: number;   // 0 or more
  available_slots: AvailableSlot[];
}

type DepartmentType = 
  | "Cardiology"
  | "Neurology"
  | "Orthopedics"
  | "Dermatology"
  | "General Medicine"
  | "Pediatrics";
```

### Success Response Definition
```typescript
interface SuccessResponse {
  status: "success";
  filter_department: DepartmentType | null;
  total_doctors: number;
  doctors: Doctor[];
}
```

### Not Found Response Definition
```typescript
interface NotFoundResponse {
  status: "not_found";
  message: string;
  doctors: [];
}
```

### Error Response Definition
```typescript
interface ErrorResponse {
  detail: string;
}
```

---

## Data Constraints

### Global Constraints
- All responses are valid JSON
- All string values are UTF-8 encoded
- All timestamps follow ISO 8601 format
- All enumerated values are case-sensitive

### Doctor Constraints
- Minimum 0, Maximum 6 doctors per response
- Each doctor must have at least 1 available slot to be included
- Doctor IDs are unique within the response

### Time Slot Constraints
- Date must be in the future or present (YYYY-MM-DD)
- Time must be within business hours (typically 08:00 to 18:00)
- Duration is typically 30 minutes
- Only one status per slot

### Department Constraints
- Exactly 6 departments available
- Department names are case-sensitive
- Filter parameter is case-insensitive (normalized internally)

---

## Validation Rules

### Request Validation
```
✓ Method: GET
✓ Query Parameter: department (optional, string)
✓ No request body required
```

### Response Validation
```
✓ Content-Type: application/json
✓ Character Set: utf-8
✓ Status Code: 200 (success/not_found) or 500 (error)
✓ Must match one of three schema definitions
```

### Doctor Count Rules
```
✓ Without filter: 0-6 doctors
✓ With department filter:
  - Matching department: 1 doctor
  - Non-matching department: 0 doctors (not_found response)
```

### Slot Count Rules
```
✓ Only "available" slots included
✓ Count matches array length
✓ Minimum slots per doctor shown: 1
✓ Typical slots per doctor: 4-6
```

---

## Examples

### Example 1: All Available Doctors
**Request:** `GET /available-slots`

**Response:**
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
        }
      ]
    }
  ]
}
```

### Example 2: Filtered by Department
**Request:** `GET /available-slots?department=Cardiology`

**Response:**
```json
{
  "status": "success",
  "filter_department": "Cardiology",
  "total_doctors": 1,
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
        }
      ]
    }
  ]
}
```

### Example 3: Department Not Found
**Request:** `GET /available-slots?department=Surgery`

**Response:**
```json
{
  "status": "not_found",
  "message": "No doctors found in Surgery department",
  "doctors": []
}
```

### Example 4: Server Error
**Request:** `GET /available-slots` (with internal error)

**Response:** (HTTP 500)
```json
{
  "detail": "Internal server error"
}
```

---

## Schema Validation

### Using JSON Schema Validators
The schema can be validated using standard JSON Schema validators:

**Python:**
```python
from jsonschema import validate

with open('available_slots_schema.json') as f:
    schema = json.load(f)

response_data = {
    "status": "success",
    "filter_department": None,
    "total_doctors": 1,
    "doctors": [...]
}

validate(instance=response_data, schema=schema)
```

**JavaScript:**
```javascript
const Ajv = require('ajv');
const schema = require('./available_slots_schema.json');

const ajv = new Ajv();
const validate = ajv.compile(schema);
const valid = validate(responseData);

if (!valid) {
  console.log(validate.errors);
}
```

**Online Tools:**
- JSON Schema Validator: https://www.jsonschemavalidator.net/
- Swagger Editor: https://editor.swagger.io/

---

## Integration with OpenAPI/Swagger

The schema can be integrated into an OpenAPI specification:

```yaml
/available-slots:
  get:
    summary: Get Available Appointment Slots
    parameters:
      - name: department
        in: query
        schema:
          type: string
          enum:
            - Cardiology
            - Neurology
            - Orthopedics
            - Dermatology
            - General Medicine
            - Pediatrics
    responses:
      '200':
        description: Successful response
        content:
          application/json:
            schema:
              $ref: 'available_slots_schema.json'
      '500':
        description: Internal server error
        content:
          application/json:
            schema:
              $ref: 'available_slots_schema.json#/definitions/ErrorResponse'
```

---

## Notes

1. **Only Available Slots**: The endpoint only returns slots with status "available". Booked slots are filtered out.

2. **Department Filter**: The department filter is case-insensitive but must match one of the 6 predefined departments.

3. **Slot Ordering**: Slots are ordered by date and time (earliest first).

4. **Doctor Ordering**: Doctors are ordered by department and experience (when multiple per department).

5. **Count Accuracy**: The `available_slots_count` always matches the length of `available_slots` array.

6. **Null Filter**: When no department filter is applied, `filter_department` is `null` (not an empty string).

---

**Last Updated:** December 17, 2025
**Schema Version:** 1.0
**Status:** ✅ Complete

