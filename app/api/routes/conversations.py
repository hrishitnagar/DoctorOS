
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_authorized_patient, get_current_user
from app.core.audit import record_audit_event
from app.database.connection import get_db

from app.models.patient import Patient
from app.models.user import User

from app.schemas.conversation import (
    ChatRequest,
    ChatResponse,
)

from app.services.conversation_service import (
    run_patient_chat,
    ConversationError,
)
from app.schemas.conversation import (
    ChatRequest,
    ChatResponse,
    ConversationHistoryResponse,
    ConversationDetailResponse,
)

from app.services.conversation_service import (
    run_patient_chat,
    get_patient_conversations,
    get_conversation_detail,
    ConversationError,
)

from app.services.rag_pipeline_service import RAGPipelineError
from app.services.citation_service import CitationValidationError


router = APIRouter(
    prefix="/patients",
    tags=["Patient Conversations"],
)


@router.post(
    "/{patient_id}/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
def chat_with_patient(
    patient_id: int,
    request: ChatRequest,
    patient: Patient = Depends(get_authorized_patient),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create or continue a patient-specific AI conversation.
    """

    try:
        result = run_patient_chat(
            db=db,
            patient_id=patient.id,
            doctor_id=current_user.id,
            question=request.question,
            conversation_id=request.conversation_id,
        )

        record_audit_event(
            db=db,
            user_id=current_user.id,
            patient_id=patient.id,
            action="READ",
            resource_type="patient_conversation",
            resource_id=str(result["conversation"].id),
            details={
                "conversation_id": result["conversation"].id,
                "question_length": len(request.question),
                "citation_count": len(
                    result["assistant_message"].citations or []
                ),
            },
        )

        return result

    except ConversationError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except (ValueError, CitationValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    except RAGPipelineError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to safely process the patient question.",
        )

    except Exception:
        logging.exception("Patient conversation endpoint failed")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to process the conversation at this time.",
        )

@router.get(
    "/{patient_id}/conversations",
    response_model=ConversationHistoryResponse,
)
def list_patient_conversations(
    patient_id: int,
    skip: int = 0,
    limit: int = 20,
    patient: Patient = Depends(get_authorized_patient),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if skip < 0:
        raise HTTPException(
            status_code=422,
            detail="Skip cannot be negative.",
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=422,
            detail="Limit must be between 1 and 100.",
        )

    conversations, total = get_patient_conversations(
        db=db,
        patient_id=patient.id,
        doctor_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    return {
        "conversations": conversations,
        "total": total,
    }

@router.get(
    "/{patient_id}/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
)
def retrieve_conversation_detail(
    patient_id: int,
    conversation_id: int,
    patient: Patient = Depends(get_authorized_patient),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        conversation = get_conversation_detail(
            db=db,
            patient_id=patient.id,
            doctor_id=current_user.id,
            conversation_id=conversation_id,
        )

        return conversation

    except ConversationError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )
