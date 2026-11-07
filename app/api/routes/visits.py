
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.visit import VisitCreate, VisitResponse
from app.services.visit_service import create_visit
from app.core.audit import record_audit_event
from app.api.deps import require_role


router = APIRouter(
    prefix="/visits",
    tags=["Visits"],
)


@router.post(
    "/",
    response_model=VisitResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_visit(
    visit_data: VisitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
):
    try:
        visit = create_visit(
            db=db,
            visit_data=visit_data,
            doctor_id=current_user.id,
        )

        record_audit_event(
            db=db,
            user_id=current_user.id,
            patient_id=visit.patient_id,
            action="CREATE",
            resource_type="visit",
            resource_id=str(visit.id),
            details={
                "appointment_id": visit.appointment_id,
                "diagnosis": visit.diagnosis,
                "medication_count": len(visit.medications),
            },
        )

        return visit

    except ValueError as exc:
        message = str(exc)

        if message in {
            "Patient not found",
            "Appointment not found",
        }:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )
