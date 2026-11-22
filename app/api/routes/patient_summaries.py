
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_authorized_patient, get_current_user
from app.core.audit import record_audit_event
from app.database.connection import get_db
from app.models.patient import Patient
from app.models.user import User

from app.schemas.conversation import (
    PatientSummaryRequest,
    PatientSummaryResponse,
)

from app.services.patient_summary_service import (
    create_or_update_patient_summary,
    get_existing_patient_summary,
)


router = APIRouter(
    prefix="/patients",
    tags=["Patient Summaries"],
)


@router.post(
    "/{patient_id}/summary",
    response_model=PatientSummaryResponse,
)
def generate_patient_summary_endpoint(
    patient_id: int,
    request: PatientSummaryRequest,
    patient: Patient = Depends(get_authorized_patient),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        summary = create_or_update_patient_summary(
            db=db,
            patient_id=patient.id,
            doctor_id=current_user.id,
            force_regenerate=request.force_regenerate,
        )

        record_audit_event(
            db=db,
            user_id=current_user.id,
            patient_id=patient.id,
            action="READ",
            resource_type="patient_summary",
            resource_id=str(summary.id),
            details={
                "summary_id": summary.id,
                "regenerated": request.force_regenerate,
            },
        )

        return summary

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except Exception:
        logging.exception("Patient summary generation failed")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to generate patient summary at this time.",
        )


@router.get(
    "/{patient_id}/summary",
    response_model=PatientSummaryResponse,
)
def retrieve_patient_summary_endpoint(
    patient_id: int,
    patient: Patient = Depends(get_authorized_patient),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    summary = get_existing_patient_summary(
        db=db,
        patient_id=patient.id,
        doctor_id=current_user.id,
    )

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No patient summary found. Generate one first.",
        )

    return summary
