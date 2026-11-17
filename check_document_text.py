
from app.database.connection import SessionLocal
from app.models.document import Document

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
        print("DOCUMENT ID:", document.id)
        print("PATIENT ID:", document.patient_id)
        print("\nEXTRACTED OCR TEXT:\n")
        print(document.raw_text)

finally:
    db.close()
