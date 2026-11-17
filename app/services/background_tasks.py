


import logging

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.document import Document

from app.services.ocr_service import process_document_ocr
from app.services.medical_extraction_service import (
    extract_and_validate_medical_data,
)
from app.services.persistence_service import (
    persist_medical_extraction,
)


logger = logging.getLogger(__name__)


def process_document_pipeline(
    db: Session,
    document: Document,
) -> dict:
    """
    Complete document processing pipeline:

    1. Extract text using OCR.
    2. Extract structured medical information.
    3. Validate extracted information.
    4. Persist validated information.
    5. Update document processing status.
    """

    document_id = document.id

    try:
        # STEP 1: OCR processing
        document = process_document_ocr(
            db=db,
            document=document,
        )

        db.refresh(document)

        if not document.raw_text or not document.raw_text.strip():
            document.extraction_status = "skipped"
            db.commit()
            db.refresh(document)

            return {
                "success": False,
                "document_id": document.id,
                "ocr_status": document.ocr_status,
                "extraction_status": document.extraction_status,
                "message": "No OCR text available. Medical extraction skipped.",
            }

        logger.info(
            "OCR completed for document_id=%s",
            document.id,
        )

        # STEP 2: Mark extraction as processing
        document.extraction_status = "processing"
        db.commit()

        # STEP 3: Extract and validate medical information
        extraction = extract_and_validate_medical_data(
            document.raw_text
        )

        logger.info(
            "Medical extraction completed for document_id=%s",
            document.id,
        )

        # STEP 4: Persist extracted information
        persistence_result = persist_medical_extraction(
            db=db,
            document_id=document.id,
            patient_id=document.patient_id,
            extraction=extraction,
        )

        # STEP 5: Mark extraction as completed
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if document is None:
            raise ValueError(
                f"Document {document_id} was not found after persistence."
            )

        document.extraction_status = "completed"
        db.commit()
        db.refresh(document)

        logger.info(
            "Document processing completed. document_id=%s",
            document_id,
        )

        return {
            "success": True,
            "document_id": document.id,
            "ocr_status": document.ocr_status,
            "extraction_status": document.extraction_status,
            "extraction": extraction.model_dump(),
            "persistence": persistence_result,
            "message": "Document processing pipeline completed successfully.",
        }

    except Exception:
        db.rollback()

        # Mark extraction as failed if processing raises an exception.
        try:
            failed_document = (
                db.query(Document)
                .filter(Document.id == document_id)
                .first()
            )

            if failed_document is not None:
                failed_document.extraction_status = "failed"
                db.commit()

        except Exception:
            db.rollback()

            logger.exception(
                "Could not update extraction status for document_id=%s",
                document_id,
            )

        logger.exception(
            "Document processing failed for document_id=%s",
            document_id,
        )

        raise


def run_ocr_background(document_id: int) -> None:
    """
    Run the complete document processing pipeline
    using a separate database session.
    """

    db = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if document is None:
            logger.error(
                "Document %s not found.",
                document_id,
            )
            return

        result = process_document_pipeline(
            db=db,
            document=document,
        )

        persistence = result.get("persistence", {})

        logger.info(
            "Background processing finished. "
            "document_id=%s success=%s extraction_status=%s "
            "entities_saved=%s lab_results_saved=%s",
            document_id,
            result.get("success"),
            result.get("extraction_status"),
            persistence.get("entities_saved", 0),
            persistence.get("lab_results_saved", 0),
        )

    except Exception:
        logger.exception(
            "Background document processing failed for document_id=%s",
            document_id,
        )

    finally:
        db.close()
