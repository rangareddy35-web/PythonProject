-- Database Backup
-- Database: ai_receptionist_3gp5
-- Date: 2025-12-28 23:10:19
-- PostgreSQL Version: PostgreSQL 18.1 (Debian 18.1-1.pgdg12+2) on x86_64-pc-linux-gnu

================================================================================

-- ENUM Types
DROP TYPE IF EXISTS action_type CASCADE;
CREATE TYPE action_type AS ENUM ('CREATE', 'READ', 'UPDATE', 'DELETE', 'BOOK', 'CANCEL');

DROP TYPE IF EXISTS appointment_status CASCADE;
CREATE TYPE appointment_status AS ENUM ('booked', 'cancelled', 'completed', 'no_show', 'pending');

DROP TYPE IF EXISTS slot_status CASCADE;
CREATE TYPE slot_status AS ENUM ('available', 'booked', 'cancelled');


-- Tables

DROP TABLE IF EXISTS appointments CASCADE;
CREATE TABLE appointments (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL,
    doctor_id CHARACTER VARYING(20) NOT NULL,
    slot_id UUID,
    reason TEXT NOT NULL,
    notes TEXT,
    status USER-DEFINED DEFAULT 'pending'::appointment_status,
    requested_datetime TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    confirmed_datetime TIMESTAMP WITHOUT TIME ZONE,
    cancelled_at TIMESTAMP WITHOUT TIME ZONE,
    cancellation_reason TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS audit_logs CASCADE;
CREATE TABLE audit_logs (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    action USER-DEFINED NOT NULL,
    appointment_id UUID,
    patient_id UUID,
    doctor_id CHARACTER VARYING(20),
    user_id CHARACTER VARYING(255),
    details TEXT NOT NULL,
    ip_address INET,
    user_agent CHARACTER VARYING(500),
    status CHARACTER VARYING(20) DEFAULT 'SUCCESS'::character varying,
    error_message TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS available_slots CASCADE;
CREATE TABLE available_slots (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    doctor_id CHARACTER VARYING(20) NOT NULL,
    date DATE NOT NULL,
    time TIME WITHOUT TIME ZONE NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 30,
    status USER-DEFINED DEFAULT 'available'::slot_status,
    notes TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS cancellation_policies CASCADE;
CREATE TABLE cancellation_policies (
    id CHARACTER VARYING(50) NOT NULL,
    doctor_id CHARACTER VARYING(20),
    hours_before_cancellation INTEGER DEFAULT 24,
    cancellation_fee NUMERIC DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS departments CASCADE;
CREATE TABLE departments (
    id CHARACTER VARYING(50) NOT NULL,
    name CHARACTER VARYING(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS doctor_working_hours CASCADE;
CREATE TABLE doctor_working_hours (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    doctor_id CHARACTER VARYING(20) NOT NULL,
    day_of_week INTEGER NOT NULL,
    start_time TIME WITHOUT TIME ZONE NOT NULL,
    end_time TIME WITHOUT TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS doctors CASCADE;
CREATE TABLE doctors (
    id CHARACTER VARYING(20) NOT NULL,
    name CHARACTER VARYING(255) NOT NULL,
    email CHARACTER VARYING(255),
    phone CHARACTER VARYING(20),
    department CHARACTER VARYING(100) NOT NULL,
    specialization CHARACTER VARYING(255) NOT NULL,
    experience INTEGER NOT NULL,
    bio TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS notifications CASCADE;
CREATE TABLE notifications (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    appointment_id UUID NOT NULL,
    patient_id UUID NOT NULL,
    notification_type CHARACTER VARYING(50) NOT NULL,
    message TEXT NOT NULL,
    is_sent BOOLEAN DEFAULT false,
    sent_at TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS patients CASCADE;
CREATE TABLE patients (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    first_name CHARACTER VARYING(100) NOT NULL,
    last_name CHARACTER VARYING(100) NOT NULL,
    email CHARACTER VARYING(255),
    phone CHARACTER VARYING(20),
    dob DATE NOT NULL,
    gender CHARACTER VARYING(10),
    blood_group CHARACTER VARYING(5),
    insurance_provider CHARACTER VARYING(255),
    insurance_id CHARACTER VARYING(50),
    allergies TEXT,
    medical_history TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Data

-- Views

CREATE OR REPLACE VIEW upcoming_appointments AS
 SELECT a.id,
    a.patient_id,
    p.first_name,
    p.last_name,
    p.email,
    a.doctor_id,
    d.name AS doctor_name,
    a.requested_datetime,
    a.status,
    a.reason
   FROM ((appointments a
     JOIN patients p ON ((a.patient_id = p.id)))
     JOIN doctors d ON (((a.doctor_id)::text = (d.id)::text)))
  WHERE ((a.status = 'booked'::appointment_status) AND (a.requested_datetime > now()))
  ORDER BY a.requested_datetime;;

CREATE OR REPLACE VIEW patient_appointment_history AS
 SELECT a.id,
    a.patient_id,
    a.doctor_id,
    d.name AS doctor_name,
    a.reason,
    a.requested_datetime,
    a.status,
    a.created_at
   FROM (appointments a
     JOIN doctors d ON (((a.doctor_id)::text = (d.id)::text)))
  ORDER BY a.created_at DESC;;

CREATE OR REPLACE VIEW doctor_availability AS
 SELECT d.id,
    d.name,
    d.department,
    count(
        CASE
            WHEN (s.status = 'available'::slot_status) THEN 1
            ELSE NULL::integer
        END) AS available_slots,
    count(
        CASE
            WHEN (s.status = 'booked'::slot_status) THEN 1
            ELSE NULL::integer
        END) AS booked_slots,
    count(s.id) AS total_slots
   FROM (doctors d
     LEFT JOIN available_slots s ON ((((d.id)::text = (s.doctor_id)::text) AND (s.date >= CURRENT_DATE))))
  WHERE (d.is_active = true)
  GROUP BY d.id, d.name, d.department
  ORDER BY (count(
        CASE
            WHEN (s.status = 'available'::slot_status) THEN 1
            ELSE NULL::integer
        END)) DESC;;

-- Functions

CREATE OR REPLACE FUNCTION public.update_appointment_timestamp()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_doctor_timestamp()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_patient_timestamp()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.book_appointment(p_patient_id uuid, p_doctor_id character varying, p_slot_id uuid, p_reason text, p_requested_datetime timestamp without time zone)
 RETURNS TABLE(success boolean, appointment_id uuid, message character varying)
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_appointment_id UUID;
BEGIN
    -- Check if slot is available
    IF NOT EXISTS (
        SELECT 1 FROM available_slots
        WHERE id = p_slot_id AND status = 'available' AND doctor_id = p_doctor_id
    ) THEN
        RETURN QUERY SELECT FALSE::BOOLEAN, NULL::UUID, 'Slot is not available'::VARCHAR;
        RETURN;
    END IF;

    -- Create appointment
    INSERT INTO appointments (patient_id, doctor_id, slot_id, reason, status, requested_datetime)
    VALUES (p_patient_id, p_doctor_id, p_slot_id, p_reason, 'booked', p_requested_datetime)
    RETURNING appointments.id INTO v_appointment_id;

    -- Update slot status
    UPDATE available_slots SET status = 'booked' WHERE id = p_slot_id;

    -- Log action
    INSERT INTO audit_logs (action, appointment_id, patient_id, doctor_id, details, status)
    VALUES ('BOOK', v_appointment_id, p_patient_id, p_doctor_id, 'Appointment booked successfully', 'SUCCESS');

    RETURN QUERY SELECT TRUE::BOOLEAN, v_appointment_id::UUID, 'Appointment booked successfully'::VARCHAR;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.cancel_appointment(p_appointment_id uuid, p_cancellation_reason text)
 RETURNS TABLE(success boolean, message character varying)
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_slot_id UUID;
BEGIN
    -- Get slot ID
    SELECT slot_id INTO v_slot_id FROM appointments WHERE id = p_appointment_id;

    -- Cancel appointment
    UPDATE appointments
    SET status = 'cancelled', cancelled_at = NOW(), cancellation_reason = p_cancellation_reason
    WHERE id = p_appointment_id AND status != 'cancelled';

    -- Update slot status back to available if slot exists
    IF v_slot_id IS NOT NULL THEN
        UPDATE available_slots SET status = 'available' WHERE id = v_slot_id;
    END IF;

    -- Log action
    INSERT INTO audit_logs (action, appointment_id, details, status)
    VALUES ('CANCEL', p_appointment_id, 'Appointment cancelled: ' || COALESCE(p_cancellation_reason, ''), 'SUCCESS');

    RETURN QUERY SELECT TRUE::BOOLEAN, 'Appointment cancelled successfully'::VARCHAR;
END;
$function$
;
