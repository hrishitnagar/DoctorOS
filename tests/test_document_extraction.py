
from app.database.connection import SessionLocal
from app.models.document import Document
from app.services.medical_extraction_service import (
    extract_and_validate_medical_data
)

db = SessionLocal()

try:
    document = db.query(Document).filter(
        Document.id == 3,
        Document.patient_id == 2
    ).first()

    if document is None:
        print("Document not found.")
    elif not document.raw_text:
        print("No OCR text available.")
    else:
        result = extract_and_validate_medical_data(
            document.raw_text
        )

        print("\nEXTRACTION RESULT:\n")
        print(result.model_dump_json(indent=4))

finally:
    db.close()
