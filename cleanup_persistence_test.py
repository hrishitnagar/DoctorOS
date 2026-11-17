
from app.database.connection import SessionLocal
from app.models.extracted_entity import ExtractedEntity
from app.models.lab_result import LabResult

db = SessionLocal()

try:
    # Remove only entities created by our synthetic test.
    deleted_entities = (
        db.query(ExtractedEntity)
        .filter(
            ExtractedEntity.document_id == 3,
            ExtractedEntity.value.in_([
                "TEST Iron Deficiency Anemia",
                "TEST Ferrous Sulphate",
                "325 mg",
                "Once daily",
                "12/11/2026",
            ])
        )
        .delete(synchronize_session=False)
    )

    # Remove only synthetic laboratory results.
    deleted_lab_results = (
        db.query(LabResult)
        .filter(
            LabResult.document_id == 3,
            LabResult.patient_id == 2,
            LabResult.test_name.in_([
                "TEST Hemoglobin",
                "TEST WBC",
            ])
        )
        .delete(synchronize_session=False)
    )

    db.commit()

    print("Synthetic entities deleted:", deleted_entities)
    print("Synthetic lab results deleted:", deleted_lab_results)
    print("Cleanup completed successfully.")

except Exception:
    db.rollback()
    raise

finally:
    db.close()
