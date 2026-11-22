
from sqlalchemy.orm import Session

from app.models.patient_summary import PatientSummary
from app.services.patient_timeline_service import get_patient_timeline
from app.services.patient_summary_generation_service import (
    generate_patient_summary,
)


def create_or_update_patient_summary(
    db: Session,
    patient_id: int,
    doctor_id: int,
    force_regenerate: bool = False,
) -> PatientSummary:
    """
    Generate a patient summary and save it.

    If a summary already exists, return it unless
    force_regenerate is True.
    """

    try:
        # Check whether a summary already exists.
        existing_summary = (
            db.query(PatientSummary)
            .filter(
                PatientSummary.patient_id == patient_id,
                PatientSummary.doctor_id == doctor_id,
            )
            .first()
        )

        # Return existing summary if regeneration is not requested.
        if existing_summary and not force_regenerate:
            return existing_summary

        # Retrieve structured patient records.
        timeline = get_patient_timeline(
            db=db,
            patient_id=patient_id,
        )

        # Generate the summary using Gemini.
        summary_text = generate_patient_summary(timeline)

        # Store references to the actual source records.
        citations = [
            {
                "record_type": record["type"],
                "record_id": record["id"],
                "date": (
                    record["date"].isoformat()
                    if record.get("date")
                    else None
                ),
                "document_id": record.get("document_id"),
            }
            for record in timeline.get("timeline", [])
        ]

        if existing_summary:
            existing_summary.summary = summary_text
            existing_summary.citations = citations

        else:
            existing_summary = PatientSummary(
                patient_id=patient_id,
                doctor_id=doctor_id,
                summary=summary_text,
                citations=citations,
            )
            db.add(existing_summary)

        db.commit()
        db.refresh(existing_summary)

        return existing_summary

    except Exception:
        db.rollback()
        raise


def get_existing_patient_summary(
    db: Session,
    patient_id: int,
    doctor_id: int,
) -> PatientSummary | None:
    """
    Retrieve an existing summary for a doctor and patient.
    """

    return (
        db.query(PatientSummary)
        .filter(
            PatientSummary.patient_id == patient_id,
            PatientSummary.doctor_id == doctor_id,
        )
        .first()
    )
