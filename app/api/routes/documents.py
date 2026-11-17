


import logging

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.api.deps import require_role
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentUploadResponse
from app.services.document_service import create_document
from app.services.background_tasks import (
    run_ocr_background,
    process_document_pipeline,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


# ---------------------------------------------------------
# Upload Document + Schedule Background OCR
# ---------------------------------------------------------

@router.post(
    "/upload/{patient_id}",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    patient_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
):
    try:
        # Save the uploaded document and create its database record
        document = await create_document(
            db=db,
            patient_id=patient_id,
            uploaded_by=current_user.id,
            file=file,
        )

        # Schedule OCR to run after the upload response is sent
        background_tasks.add_task(
            run_ocr_background,
            document.id,
        )

        logger.info(
            "Document uploaded successfully. document_id=%s",
            document.id,
        )

        # Return immediately with the initial OCR status
        return document

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception:
        logger.exception("Document upload failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document upload failed",
        )


# ---------------------------------------------------------
# Manual OCR Processing Endpoint
# ---------------------------------------------------------




@router.post("/{document_id}/process-ocr")
def process_document_ocr_endpoint(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    try:
        result = process_document_pipeline(
            db=db,
            document=document,
        )

        db.refresh(document)

        persistence = result.get("persistence", {})

        return {
            "message": result.get("message"),
            "document_id": document.id,
            "ocr_status": document.ocr_status,
            "extraction_status": document.extraction_status,
            "success": result.get("success", False),
            "entities_saved": persistence.get("entities_saved", 0),
            "lab_results_saved": persistence.get("lab_results_saved", 0),
        }

    except Exception:
        logger.exception(
            "Document processing failed for document_id=%s",
            document_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document processing failed",
        )
