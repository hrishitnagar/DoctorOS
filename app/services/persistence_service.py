
from datetime import datetime, date

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.extracted_entity import ExtractedEntity
from app.models.lab_result import LabResult
from app.schemas.medical_extraction import MedicalExtractionResult


def parse_medical_date(value: str) -> date | None:
    """
    Convert supported date formats into Python date objects.
    Return None when the date cannot be parsed.
    """
    supported_formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
    ]

    for date_format in supported_formats:
        try:
            return datetime.strptime(value.strip(), date_format).date()
        except ValueError:
            continue

    return None


def save_extracted_entity(
    db: Session,
    document_id: int,
    entity_type: str,
    value: str,
    confidence: float | None = None,
    unit: str | None = None,
) -> bool:
    """
    Save an extracted entity only if an identical record
    does not already exist for this document.
    """

    existing_entity = db.query(ExtractedEntity).filter(
        ExtractedEntity.document_id == document_id,
        ExtractedEntity.entity_type == entity_type,
        ExtractedEntity.value == value,
        ExtractedEntity.unit == unit,
    ).first()

    if existing_entity:
        return False

    entity = ExtractedEntity(
        document_id=document_id,
        entity_type=entity_type,
        value=value,
        confidence=confidence,
        unit=unit,
        needs_review=True,
    )

    db.add(entity)
    return True


def save_lab_result(
    db: Session,
    patient_id: int,
    document_id: int,
    lab_test,
    test_date: date | None = None,
) -> bool:
    """
    Save a laboratory result if an identical record
    does not already exist for this document.
    """

    existing_result = db.query(LabResult).filter(
        LabResult.document_id == document_id,
        LabResult.patient_id == patient_id,
        LabResult.test_name == lab_test.name,
        LabResult.value == lab_test.value,
        LabResult.unit == lab_test.unit,
        LabResult.test_date == test_date,
    ).first()

    if existing_result:
        return False

    result = LabResult(
        patient_id=patient_id,
        document_id=document_id,
        test_name=lab_test.name,
        value=lab_test.value,
        unit=lab_test.unit,
        ref_range=lab_test.reference_range,
        test_date=test_date,
        confidence=lab_test.confidence,
        needs_review=True,
    )

    db.add(result)
    return True


def persist_medical_extraction(
    db: Session,
    document_id: int,
    patient_id: int,
    extraction: MedicalExtractionResult,
) -> dict:
    """
    Persist validated medical extraction results.

    All records are committed in one transaction.
    If an error occurs, the transaction is rolled back.
    """

    try:
        # 1. Verify that the document exists and belongs
        #    to the supplied patient.
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.patient_id == patient_id,
        ).first()

        if document is None:
            raise ValueError(
                "Document not found or does not belong to this patient."
            )

        saved_entities = 0
        saved_lab_results = 0

        # 2. Save diagnoses.
        for diagnosis in extraction.diagnoses:
            if save_extracted_entity(
                db=db,
                document_id=document_id,
                entity_type="diagnosis",
                value=diagnosis.name,
                confidence=diagnosis.confidence,
            ):
                saved_entities += 1

        # 3. Save medicines, doses and frequencies.
        for medicine in extraction.medicines:

            if save_extracted_entity(
                db=db,
                document_id=document_id,
                entity_type="medicine",
                value=medicine.name,
                confidence=medicine.confidence,
            ):
                saved_entities += 1

            if medicine.dose:
                if save_extracted_entity(
                    db=db,
                    document_id=document_id,
                    entity_type="medicine_dose",
                    value=medicine.dose,
                    confidence=medicine.confidence,
                ):
                    saved_entities += 1

            if medicine.frequency:
                if save_extracted_entity(
                    db=db,
                    document_id=document_id,
                    entity_type="medicine_frequency",
                    value=medicine.frequency,
                    confidence=medicine.confidence,
                ):
                    saved_entities += 1

        # 4. Save dates as extracted entities.
        #    We do not assume a report date is a lab test date.
        for extracted_date in extraction.dates:
            if save_extracted_entity(
                db=db,
                document_id=document_id,
                entity_type=extracted_date.type,
                value=extracted_date.value,
            ):
                saved_entities += 1

        # 5. Find an explicitly identified lab test date.
        lab_test_date = None

        for extracted_date in extraction.dates:
            if extracted_date.type.lower() in {
                "test_date",
                "lab_test_date",
            }:
                lab_test_date = parse_medical_date(
                    extracted_date.value
                )
                if lab_test_date is not None:
                    break

        # 6. Save laboratory results.
        for lab_test in extraction.lab_tests:
            if save_lab_result(
                db=db,
                patient_id=patient_id,
                document_id=document_id,
                lab_test=lab_test,
                test_date=lab_test_date,
            ):
                saved_lab_results += 1

        # 7. Commit everything together.
        db.commit()

        return {
            "success": True,
            "document_id": document_id,
            "patient_id": patient_id,
            "entities_saved": saved_entities,
            "lab_results_saved": saved_lab_results,
            "message": "Medical extraction data saved successfully.",
        }

    except Exception:
        db.rollback()
        raise
