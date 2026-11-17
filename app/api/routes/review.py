
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.deps import require_role
from app.models.user import User

from app.schemas.review import (
    ExtractedEntityUpdate,
    LabResultUpdate,
    ReviewDecision,
)

from app.services.review_service import (
    get_pending_reviews,
    correct_extracted_entity,
    correct_lab_result,
    review_extracted_entity,
    review_lab_result,
)


router = APIRouter(
    prefix="/review",
    tags=["Medical Record Review"],
    dependencies=[Depends(require_role("doctor"))],
)


def handle_review_error(error: Exception):
    if isinstance(error, LookupError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    if isinstance(error, PermissionError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )

    if isinstance(error, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    raise error


@router.get("/pending/{document_id}")
def pending_reviews(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
):
    try:
        return get_pending_reviews(
            db=db,
            document_id=document_id,
            doctor=current_user,
        )
    except (LookupError, PermissionError, ValueError) as error:
        handle_review_error(error)


@router.patch("/entities/{entity_id}")
def update_entity(
    entity_id: int,
    payload: ExtractedEntityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
):
    try:
        entity = correct_extracted_entity(
            db=db,
            entity_id=entity_id,
            doctor=current_user,
            updates=payload.model_dump(exclude_unset=True),
        )

        return {
            "message": "Extracted entity corrected successfully.",
            "entity_id": entity.id,
            "value": entity.value,
            "unit": entity.unit,
            "review_status": entity.review_status,
        }

    except (LookupError, PermissionError, ValueError) as error:
        handle_review_error(error)


@router.patch("/lab-results/{lab_id}")
def update_lab_result(
    lab_id: int,
    payload: LabResultUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
):
    try:
        lab = correct_lab_result(
            db=db,
            lab_id=lab_id,
            doctor=current_user,
            updates=payload.model_dump(exclude_unset=True),
        )

        return {
            "message": "Lab result corrected successfully.",
            "lab_id": lab.id,
            "test_name": lab.test_name,
            "value": lab.value,
            "unit": lab.unit,
            "ref_range": lab.ref_range,
            "test_date": (
                lab.test_date.isoformat()
                if lab.test_date else None
            ),
            "review_status": lab.review_status,
        }

    except (LookupError, PermissionError, ValueError) as error:
        handle_review_error(error)


@router.post("/entities/{entity_id}/decision")
def decide_entity(
    entity_id: int,
    payload: ReviewDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
):
    try:
        entity = review_extracted_entity(
            db=db,
            entity_id=entity_id,
            doctor=current_user,
            decision=payload.decision,
        )

        return {
            "message": f"Extracted entity {payload.decision}.",
            "entity_id": entity.id,
            "review_status": entity.review_status,
            "needs_review": entity.needs_review,
            "reviewed_by": entity.reviewed_by,
            "reviewed_at": (
                entity.reviewed_at.isoformat()
                if entity.reviewed_at else None
            ),
        }

    except (LookupError, PermissionError, ValueError) as error:
        handle_review_error(error)


@router.post("/lab-results/{lab_id}/decision")
def decide_lab_result(
    lab_id: int,
    payload: ReviewDecision,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
):
    try:
        lab = review_lab_result(
            db=db,
            lab_id=lab_id,
            doctor=current_user,
            decision=payload.decision,
        )

        return {
            "message": f"Lab result {payload.decision}.",
            "lab_id": lab.id,
            "review_status": lab.review_status,
            "needs_review": lab.needs_review,
            "reviewed_by": lab.reviewed_by,
            "reviewed_at": (
                lab.reviewed_at.isoformat()
                if lab.reviewed_at else None
            ),
        }

    except (LookupError, PermissionError, ValueError) as error:
        handle_review_error(error)
