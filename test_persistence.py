
from app.database.connection import SessionLocal
from app.services.persistence_service import (
    persist_medical_extraction
)
from app.services.medical_extraction_service import (
    extract_and_validate_medical_data
)
from app.models.document import Document

db = SessionLocal()

try:
    document = db.query(Document).filter(
        Document.id == 3,
        Document.patient_id == 2
    ).first()

    if document is None:
        raise ValueError("Document not found.")

    extraction = extract_and_validate_medical_data(
        document.raw_text
    )

    result = persist_medical_extraction(
        db=db,
        document_id=document.id,
        patient_id=document.patient_id,
        extraction=extraction
    )

    print("\nPERSISTENCE RESULT:")
    print(result)

finally:
    db.close()

