
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_authorized_patient
from app.core.audit import record_audit_event
from app.database.connection import get_db
from app.models.patient import Patient
from app.models.user import User
from app.api.deps import get_current_user

from app.schemas.rag import RAGAskRequest, RAGAskResponse
from app.services.rag_pipeline_service import (
    run_rag_pipeline,
    RAGPipelineError,
)
from app.services.citation_service import CitationValidationError


router = APIRouter(
    prefix="/patients",
    tags=["RAG - Patient Q&A"],
)


@router.post(
    "/{patient_id}/ask",
    response_model=RAGAskResponse,
    status_code=status.HTTP_200_OK,
)
def ask_patient_question(
    patient_id: int,
    request: RAGAskRequest,
    patient: Patient = Depends(get_authorized_patient),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Answer a doctor's question using authorized patient documents.
    """

    try:
        result = run_rag_pipeline(
            db=db,
            patient_id=patient.id,
            question=request.question,
        )

        # Record the AI-assisted patient record access.
        record_audit_event(
            db=db,
            user_id=current_user.id,
            patient_id=patient.id,
            action="READ",
            resource_type="patient_rag",
            resource_id=str(patient.id),
            details={
                "question": request.question,
                "retrieved_chunks": result["retrieved_chunks"],
                "citation_count": len(result["citations"]),
            },
        )

        return result

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

    except Exception as exc:
       import logging
       logging.exception("RAG endpoint failed")
       raise HTTPException(
         status_code=503,
         detail=f"RAG service error: {type(exc).__name__}: {str(exc)}"
       )
