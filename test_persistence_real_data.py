
from app.database.connection import SessionLocal
from app.models.extracted_entity import ExtractedEntity
from app.models.lab_result import LabResult

from app.schemas.medical_extraction import (
    DiagnosisExtraction,
    MedicineExtraction,
    LabTestExtraction,
    DateExtraction,
    MedicalExtractionResult,
)

from app.services.persistence_service import (
    persist_medical_extraction,
)


DOCUMENT_ID = 3
PATIENT_ID = 2


# Synthetic medical information for testing only.
extraction = MedicalExtractionResult(
    diagnoses=[
        DiagnosisExtraction(
            name="TEST Iron Deficiency Anemia",
            confidence=0.95,
            needs_review=True,
        )
    ],
    medicines=[
        MedicineExtraction(
            name="TEST Ferrous Sulphate",
            dose="325 mg",
            frequency="Once daily",
            confidence=0.95,
            needs_review=True,
        )
    ],
    lab_tests=[
        LabTestExtraction(
            name="TEST Hemoglobin",
            value=11.2,
            unit="g/dL",
            reference_range="13.0 - 17.0 g/dL",
            confidence=0.95,
            needs_review=True,
        ),
        LabTestExtraction(
            name="TEST WBC",
            value=7500.0,
            unit="cells/mcL",
            reference_range="4000 - 11000 cells/mcL",
            confidence=0.95,
            needs_review=True,
        ),
    ],
    dates=[
        DateExtraction(
            value="12/11/2026",
            type="report_date",
        ),
        DateExtraction(
            value="12/11/2026",
            type="test_date",
        ),
    ],
)


db = SessionLocal()

try:
    print("\n========== FIRST PERSISTENCE RUN ==========")

    first_result = persist_medical_extraction(
        db=db,
        document_id=DOCUMENT_ID,
        patient_id=PATIENT_ID,
        extraction=extraction,
    )

    print(first_result)

    print("\n========== SECOND PERSISTENCE RUN ==========")

    second_result = persist_medical_extraction(
        db=db,
        document_id=DOCUMENT_ID,
        patient_id=PATIENT_ID,
        extraction=extraction,
    )

    print(second_result)

    # Verify extracted entities.
    entities = db.query(ExtractedEntity).filter(
        ExtractedEntity.document_id == DOCUMENT_ID,
        ExtractedEntity.value.in_([
            "TEST Iron Deficiency Anemia",
            "TEST Ferrous Sulphate",
            "325 mg",
            "Once daily",
            "12/11/2026",
        ]),
    ).all()

    # Verify laboratory results.
    lab_results = db.query(LabResult).filter(
        LabResult.document_id == DOCUMENT_ID,
        LabResult.patient_id == PATIENT_ID,
        LabResult.test_name.in_([
            "TEST Hemoglobin",
            "TEST WBC",
        ]),
    ).all()

    print("\n========== DATABASE VERIFICATION ==========")

    print("Extracted entities found:", len(entities))
    print("Lab results found:", len(lab_results))

    for entity in entities:
        print(
            entity.entity_type,
            "|",
            entity.value,
            "| Review:",
            entity.needs_review,
        )

    for result in lab_results:
        print(
            result.test_name,
            "| Value:",
            result.value,
            "| Unit:",
            result.unit,
            "| Test date:",
            result.test_date,
            "| Review:",
            result.needs_review,
        )

    # Basic assertions.
    assert first_result["success"] is True
    assert second_result["success"] is True

    assert second_result["entities_saved"] == 0
    assert second_result["lab_results_saved"] == 0

    assert len(entities) == 6
    assert len(lab_results) == 2

    assert all(entity.needs_review for entity in entities)
    assert all(result.needs_review for result in lab_results)

    assert all(
        result.test_date is not None
        for result in lab_results
    )

    print("\nALL PERSISTENCE TESTS PASSED!")

finally:
    db.close()
