
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.patient import Patient
from app.schemas.appointment import AppointmentCreate


APPOINTMENT_DURATION_MINUTES = 30


def create_appointment(
    db: Session,
    appointment_data: AppointmentCreate,
    doctor_id: int,
) -> Appointment:
    """
    Create an appointment after checking for overlapping
    appointments for the same doctor.

    Each appointment is assumed to last 30 minutes.
    """

    start_time = appointment_data.appointment_datetime.astimezone(
        timezone.utc
    )

    end_time = start_time + timedelta(
        minutes=APPOINTMENT_DURATION_MINUTES
    )

    # Verify that the patient exists.
    patient = (
        db.query(Patient)
        .filter(Patient.id == appointment_data.patient_id)
        .first()
    )

    if not patient:
        raise ValueError("Patient not found")

    # Find existing appointments that overlap this time slot.
    # Cancelled appointments do not block the slot.
    overlapping_appointment = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status != "cancelled",
            Appointment.appointment_datetime < end_time,
            Appointment.appointment_datetime
            + timedelta(minutes=APPOINTMENT_DURATION_MINUTES)
            > start_time,
        )
        .first()
    )

    if overlapping_appointment:
        raise ValueError(
            "Doctor already has an appointment during this time slot"
        )

    appointment = Appointment(
        patient_id=appointment_data.patient_id,
        doctor_id=doctor_id,
        appointment_datetime=start_time,
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
