
from app.database.connection import SessionLocal
from app.models.document import Document
from app.models.extracted_entity import ExtractedEntity
from app.models.lab_result import LabResult

db = SessionLocal()

try:
    document = db.query(Document).filter(Document.id == 4).first()

    if document is None:
        print("Document 4 not found.")
    else:
        print("DOCUMENT STATUS")
        print("Document ID:", document.id)
        print("Patient ID:", document.patient_id)
        print("OCR Status:", document.ocr_status)
        print("Extraction Status:", document.extraction_status)

        entities = (
            db.query(ExtractedEntity)
            .filter(ExtractedEntity.document_id == 4)
            .all()
        )

        lab_results = (
            db.query(LabResult)
            .filter(LabResult.document_id == 4)
            .all()
        )

        print("\nEXTRACTED ENTITIES:", len(entities))

        for entity in entities:
            print(
                entity.entity_type,
                entity.value,
                "Needs review:",
                entity.needs_review
            )

        print("\nLAB RESULTS:", len(lab_results))

        for lab in lab_results:
            print(
                lab.test_name,
                lab.value,
                lab.unit,
                "Needs review:",
                lab.needs_review
            )

finally:
    db.close()
