
from app.database.connection import SessionLocal
from app.models.document import Document

db = SessionLocal()

try:
    documents = (
        db.query(Document)
        .order_by(Document.id.desc())
        .limit(10)
        .all()
    )

    for document in documents:
        print(
            f"Document ID: {document.id} | "
            f"Patient ID: {document.patient_id} | "
            f"OCR: {document.ocr_status} | "
            f"Extraction: {document.extraction_status}"
        )

finally:
    db.close()
