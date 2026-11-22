


import logging

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.document import Document

from app.services.ocr_service import process_document_ocr
from app.services.chunking_service import create_document_chunks

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
    2. Generate page-aware RAG chunks.
    3. Extract structured medical information.
    4. Validate extracted information.
    5. Persist validated information.
    6. Update document processing status.

    Chunking failure does not stop medical extraction.
    """

    document_id = document.id
    chunking_result = {
        "success": False,
        "chunks_created": 0,
        "message": "Chunking not attempted.",
    }

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
                "chunking": chunking_result,
                "message": "No OCR text available. Medical extraction skipped.",
            }

        logger.info(
            "OCR completed for document_id=%s",
            document.id,
        )

        # STEP 2: Generate and persist RAG chunks
        try:
            chunks_created = create_document_chunks(
                db=db,
                document=document,
            )

            chunking_result = {
                "success": True,
                "chunks_created": chunks_created,
                "message": "Document chunks created successfully.",
            }

            logger.info(
                "Chunking completed for document_id=%s, chunks=%s",
                document.id,
                chunks_created,
            )

        except Exception as chunking_error:
            db.rollback()

            chunking_result = {
                "success": False,
                "chunks_created": 0,
                "message": str(chunking_error),
            }

            logger.exception(
                "Chunking failed for document_id=%s. "
                "Continuing medical extraction.",
                document_id,
            )

        # Reload document after chunking transaction.
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if document is None:
            raise ValueError(
                f"Document {document_id} was not found after chunking."
            )

        # STEP 3: Mark extraction as processing
        document.extraction_status = "processing"
        db.commit()

        # STEP 4: Extract and validate medical information
        extraction = extract_and_validate_medical_data(
            document.raw_text
        )

        logger.info(
            "Medical extraction completed for document_id=%s",
            document.id,
        )

        # STEP 5: Persist extracted information
        persistence_result = persist_medical_extraction(
            db=db,
            document_id=document.id,
            patient_id=document.patient_id,
            extraction=extraction,
        )

        # STEP 6: Mark extraction as completed
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
            "chunking": chunking_result,
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
        chunking = result.get("chunking", {})

        logger.info(
            "Background processing finished. "
            "document_id=%s success=%s extraction_status=%s "
            "chunks_created=%s entities_saved=%s lab_results_saved=%s",
            document_id,
            result.get("success"),
            result.get("extraction_status"),
            chunking.get("chunks_created", 0),
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

