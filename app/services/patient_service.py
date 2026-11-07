
from datetime import date
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.patient import Patient
from app.schemas.patient import PatientCreate


def create_patient(db: Session, patient_data: PatientCreate) -> Patient:
    """
    Create a patient and generate a unique patient UID.

    Format:
    DOS-YYYY-000001
    """
    
def get_patients(
    db: Session,
    search: str | None = None,
    skip: int = 0,
    limit: int = 10,
):
    query = db.query(Patient)

    if search:
        search_term = f"%{search.strip()}%"

        query = query.filter(
            or_(
                Patient.name.ilike(search_term),
                Patient.phone.ilike(search_term),
                Patient.patient_uid.ilike(search_term),
            )
        )

    total = query.count()

    patients = (
        query
        .order_by(Patient.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return patients, total


    current_year = date.today().year

    # A temporary unique value lets PostgreSQL assign the patient ID.
    temporary_uid = f"T-{uuid4().hex[:20]}"

    patient = Patient(
        **patient_data.model_dump(),
        patient_uid=temporary_uid,
    )

    try:
        db.add(patient)

        # Insert the patient and obtain its database-generated ID.
        db.flush()

        # Use the unique database ID to generate the permanent patient UID.
        patient.patient_uid = (
            f"DOS-{current_year}-{patient.id:06d}"
        )

        db.commit()
        db.refresh(patient)

        return patient

    except Exception:
        db.rollback()
        raise
