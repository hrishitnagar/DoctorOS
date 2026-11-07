
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.visit import Visit
from app.models.medication import Medication
from app.schemas.visit import VisitCreate


def create_visit(
    db: Session,
    visit_data: VisitCreate,
    doctor_id: int,
) -> Visit:
    # Confirm that the patient exists
    patient = (
        db.query(Patient)
        .filter(Patient.id == visit_data.patient_id)
        .first()
    )

    if not patient:
        raise ValueError("Patient not found")

    # If an appointment is supplied, validate its ownership and patient
    if visit_data.appointment_id is not None:
        appointment = (
            db.query(Appointment)
            .filter(
                Appointment.id == visit_data.appointment_id,
                Appointment.doctor_id == doctor_id,
            )
            .first()
        )

        if not appointment:
            raise ValueError("Appointment not found")

        if appointment.patient_id != visit_data.patient_id:
            raise ValueError(
                "Appointment does not belong to this patient"
            )

        if appointment.status != "completed":
            raise ValueError(
                "Visit can only be recorded for a completed appointment"
            )

        # The appointment can only have one visit
        existing_visit = (
            db.query(Visit)
            .filter(Visit.appointment_id == appointment.id)
            .first()
        )

        if existing_visit:
            raise ValueError(
                "A visit is already recorded for this appointment"
            )

    # Create the visit
    visit = Visit(
        appointment_id=visit_data.appointment_id,
        patient_id=visit_data.patient_id,
        doctor_id=doctor_id,
        observations=visit_data.observations,
        diagnosis=visit_data.diagnosis,
        prescription_notes=visit_data.prescription_notes,
        visit_date=visit_data.visit_date,
    )

    try:
        db.add(visit)
        db.flush()  # Generates visit.id before adding medications

        # Add the prescribed medications
        for medication_data in visit_data.medications:
            medication = Medication(
                visit_id=visit.id,
                drug=medication_data.drug,
                dose=medication_data.dose,
                frequency=medication_data.frequency,
                duration=medication_data.duration,
                instructions=medication_data.instructions,
            )
            db.add(medication)

        db.commit()
        db.refresh(visit)

        return visit

    except Exception:
        db.rollback()
        raise
