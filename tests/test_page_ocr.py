
from app.database.connection import SessionLocal
from app.models.document import Document
from app.services.ocr_service import extract_pages_from_file

db = SessionLocal()

try:
    document = db.query(Document).filter(
        Document.id == 4
    ).first()

    if document is None:
        print("Document ID 4 not found.")
    else:
        print("Document ID:", document.id)
        print("Patient ID:", document.patient_id)
        print("File:", document.file_path)

        pages = extract_pages_from_file(document.file_path)

        print("\nTotal pages:", len(pages))

        for page_number, page_text in pages:
            print(f"\n--- PAGE {page_number} ---")
            print("Characters:", len(page_text))
            print("Preview:", page_text[:300])

        if pages and all(number >= 1 for number, _ in pages):
            print("\nPAGE-AWARE OCR TEST PASSED")
        else:
            print("\nPAGE-AWARE OCR TEST FAILED")

finally:
    db.close()
