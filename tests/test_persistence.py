
from datetime import datetime, timezone

from app.models.user import User
from app.models.patient import Patient
from app.models.document import Document
from app.models.extracted_entity import ExtractedEntity
from app.models.lab_result import LabResult

from app.schemas.medical_extraction import (
    MedicalExtractionResult,
    DiagnosisExtraction,
    MedicineExtraction,
    LabTestExtraction,
    DateExtraction,
)

from app.services.persistence_service import (
    persist_medical_extraction,
)


def test_persist_medical_extraction(db):
    # 1. Create a synthetic doctor.
    doctor = User(
        name="Persistence Test Doctor",
        email="persistence-test-doctor@example.com",
        password_hash="synthetic-test-hash",
        role="doctor",
    )

    db.add(doctor)
    db.flush()

    # 2. Create a synthetic patient.
    patient = Patient(
        patient_uid="DOS-PERSISTENCE-TEST-001",
        name="Synthetic Persistence Patient",
    )

    db.add(patient)
    db.flush()

    # 3. Create a synthetic document.
    document = Document(
        patient_id=patient.id,
        document_type="test_report",
        file_path="synthetic/persistence_test.pdf",
        uploaded_by=doctor.id,
        uploaded_at=datetime.now(timezone.utc),
        ocr_status="done",
        extraction_status="done",
        raw_text="Synthetic laboratory report for testing.",
    )

    db.add(document)
    db.flush()

    # 4. Prepare mock structured extraction data.
    extraction = MedicalExtractionResult(
        diagnoses=[
            DiagnosisExtraction(
                name="Iron Deficiency Anemia",
                confidence=0.95,
            )
        ],
        medicines=[
            MedicineExtraction(
                name="Ferrous Sulphate",
                dose="325 mg",
                frequency="Once daily",
                confidence=0.92,
            )
        ],
        lab_tests=[
            LabTestExtraction(
                name="Hemoglobin",
                value=11.2,
                unit="g/dL",
                reference_range="13.0 - 17.0 g/dL",
                confidence=0.98,
            )
        ],
        dates=[
            DateExtraction(
                value="12/11/2026",
                type="test_date",
            )
        ],
    )

    # 5. Persist the extraction.
    result = persist_medical_extraction(
        db=db,
        document_id=document.id,
        patient_id=patient.id,
        extraction=extraction,
    )

    print("\nPERSISTENCE RESULT:")
    print(result)

    assert result["success"] is True
    assert result["document_id"] == document.id
    assert result["patient_id"] == patient.id

    # 6. Verify saved entities and laboratory results.
    entities = (
        db.query(ExtractedEntity)
        .filter(ExtractedEntity.document_id == document.id)
        .all()
    )

    lab_results = (
        db.query(LabResult)
        .filter(
            LabResult.document_id == document.id,
            LabResult.patient_id == patient.id,
        )
        .all()
    )

    assert len(entities) == 5
    assert len(lab_results) == 1

    assert all(entity.needs_review for entity in entities)
    assert all(lab.needs_review for lab in lab_results)

    # 7. Verify duplicate records are not inserted.
    second_result = persist_medical_extraction(
        db=db,
        document_id=document.id,
        patient_id=patient.id,
        extraction=extraction,
    )

    assert second_result["entities_saved"] == 0
    assert second_result["lab_results_saved"] == 0

    assert (
        db.query(ExtractedEntity)
        .filter(ExtractedEntity.document_id == document.id)
        .count()
        == 5
    )

    assert (
        db.query(LabResult)
        .filter(
            LabResult.document_id == document.id,
            LabResult.patient_id == patient.id,
        )
        .count()
        == 1
    )


