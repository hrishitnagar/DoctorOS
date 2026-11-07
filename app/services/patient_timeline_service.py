
from datetime import date, datetime, time, timezone

from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.visit import Visit
from app.models.document import Document
from app.models.lab_result import LabResult


def _timeline_sort_key(value: datetime | date) -> datetime:
    """
    Convert timeline dates to UTC-aware datetimes for consistent sorting.
    Lab results use a date, so they are placed at midnight UTC.
    """
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            value = value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    return datetime.combine(
        value,
        time.min,
        tzinfo=timezone.utc,
    )


def get_patient_timeline(
    db: Session,
    patient_id: int,
) -> dict:
    # Confirm that the patient exists
    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if not patient:
        raise ValueError("Patient not found")

    visits = (
        db.query(Visit)
        .filter(Visit.patient_id == patient_id)
        .all()
    )

    documents = (
        db.query(Document)
        .filter(Document.patient_id == patient_id)
        .all()
    )

    lab_results = (
        db.query(LabResult)
        .filter(LabResult.patient_id == patient_id)
        .all()
    )

    timeline = []

    # Add visits
    for visit in visits:
        timeline.append({
            "type": "visit",
            "id": visit.id,
            "date": visit.visit_date,
            "appointment_id": visit.appointment_id,
            "doctor_id": visit.doctor_id,
            "observations": visit.observations,
            "diagnosis": visit.diagnosis,
            "prescription_notes": visit.prescription_notes,
            "medications": [
                {
                    "id": medication.id,
                    "drug": medication.drug,
                    "dose": medication.dose,
                    "frequency": medication.frequency,
                    "duration": medication.duration,
                    "instructions": medication.instructions,
                }
                for medication in visit.medications
            ],
        })

    # Add documents
    for document in documents:
        timeline.append({
            "type": "document",
            "id": document.id,
            "date": document.uploaded_at,
            "document_type": document.document_type,
            "ocr_status": document.ocr_status,
        })

    # Add lab results
    for result in lab_results:
        timeline.append({
            "type": "lab_result",
            "id": result.id,
            "date": result.test_date,
            "document_id": result.document_id,
            "test_name": result.test_name,
            "value": result.value,
            "unit": result.unit,
            "ref_range": result.ref_range,
        })

    # Newest records first
    timeline.sort(
        key=lambda item: _timeline_sort_key(item["date"]),
        reverse=True,
    )

    return {
        "patient_id": patient.id,
        "patient_uid": patient.patient_uid,
        "patient_name": patient.name,
        "total_records": len(timeline),
        "timeline": timeline,
    }
