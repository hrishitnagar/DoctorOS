
from datetime import timedelta, timezone

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.patient import Patient
from app.schemas.appointment import AppointmentCreate


def create_appointment(
    db: Session,
    appointment_data: AppointmentCreate,
    doctor_id: int,
) -> Appointment:
    """
    Create an appointment after checking for overlapping
    appointments for the same doctor.
    """

    # Convert the requested time to UTC.
    start_time = appointment_data.appointment_datetime.astimezone(
        timezone.utc
    )

    end_time = start_time + timedelta(
        minutes=appointment_data.duration_minutes
    )

    # 1. Verify that the patient exists.
    patient = (
        db.query(Patient)
        .filter(Patient.id == appointment_data.patient_id)
        .first()
    )

    if not patient:
        raise ValueError("Patient not found")

    # 2. Check for overlapping appointments.
    existing_appointments = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status.notin_(["cancelled"]),
        )
        .all()
    )

    for existing in existing_appointments:
        existing_start = existing.appointment_datetime

        # Handle PostgreSQL timestamps returned as timezone-aware values.
        if existing_start.tzinfo is None:
            existing_start = existing_start.replace(tzinfo=timezone.utc)
        else:
            existing_start = existing_start.astimezone(timezone.utc)

        existing_end = existing_start + timedelta(
            minutes=existing.duration_minutes
        )

        # Standard interval-overlap condition.
        if existing_start < end_time and existing_end > start_time:
            raise ValueError(
                "Doctor already has an appointment during this time slot"
            )

    # 3. Create the appointment.
    appointment = Appointment(
        patient_id=appointment_data.patient_id,
        doctor_id=doctor_id,
        appointment_datetime=start_time,
        duration_minutes=appointment_data.duration_minutes,
        status="scheduled",
        reason=appointment_data.reason,
    )

    try:
        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        return appointment

    except Exception:
        db.rollback()
        raise
