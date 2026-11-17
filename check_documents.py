
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

    if not documents:
        print("No documents found.")

    for document in documents:
        print(
            f"Document ID: {document.id} | "
            f"Patient ID: {document.patient_id} | "
            f"OCR Status: {document.ocr_status}"
        )

finally:
    db.close()
