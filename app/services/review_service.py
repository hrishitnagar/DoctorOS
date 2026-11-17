

from datetime import datetime, timezone
from math import isfinite

from sqlalchemy.orm import Session

from app.models.extracted_entity import ExtractedEntity
from app.models.lab_result import LabResult
from app.models.document import Document
from app.models.user import User
from app.models.audit_log import AuditLog


def _now():
    return datetime.now(timezone.utc)


def _serialize(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _create_audit_log(
    db: Session,
    doctor: User,
    patient_id: int,
    action: str,
    resource_type: str,
    resource_id: int,
    details: dict,
):
    log = AuditLog(
        user_id=doctor.id,
        patient_id=patient_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        details=details,
        timestamp=_now(),
    )
    db.add(log)


def _ensure_doctor(doctor: User):
    if not doctor.is_active or doctor.role.lower() != "doctor":
        raise PermissionError(
            "Only active doctors can review medical records."
        )


def _ensure_pending(record):
    if record.review_status != "pending":
        raise ValueError(
            f"This record has already been {record.review_status}."
        )


def _save_changes(
    db: Session,
    record,
    doctor: User,
    patient_id: int,
    resource_type: str,
    updates: dict,
):
    allowed_fields = (
        {"value", "unit"}
        if resource_type == "extracted_entity"
        else {"test_name", "value", "unit", "ref_range", "test_date"}
    )

    if not updates:
        raise ValueError("At least one field must be supplied.")

    invalid_fields = set(updates) - allowed_fields

    if invalid_fields:
        raise ValueError(
            f"Fields cannot be edited: {', '.join(sorted(invalid_fields))}"
        )

    _ensure_doctor(doctor)
    _ensure_pending(record)

    old_values = {}
    new_values = {}

    try:
        for field, new_value in updates.items():

            if isinstance(new_value, str):
                new_value = new_value.strip()

            if isinstance(new_value, str) and not new_value:
                raise ValueError(f"{field} cannot be empty.")

            # Numeric validation applies only to laboratory values.
            if field == "value" and resource_type == "lab_result":
                try:
                    new_value = float(new_value)
                except (ValueError, TypeError):
                    raise ValueError(
                        "Lab result value must be numeric."
                    )

                if not isfinite(new_value):
                    raise ValueError(
                        "Value must be a finite number."
                    )

            old_value = getattr(record, field)

            if old_value != new_value:
                old_values[field] = _serialize(old_value)
                new_values[field] = _serialize(new_value)
                setattr(record, field, new_value)

        if not new_values:
            raise ValueError("No changes were supplied.")

        _create_audit_log(
            db=db,
            doctor=doctor,
            patient_id=patient_id,
            action="medical_record_corrected",
            resource_type=resource_type,
            resource_id=record.id,
            details={
                "before": old_values,
                "after": new_values,
            },
        )

        db.commit()
        db.refresh(record)

        return record

    except Exception:
        db.rollback()
        raise


def correct_extracted_entity(
    db: Session,
    entity_id: int,
    doctor: User,
    updates: dict,
):
    _ensure_doctor(doctor)

    entity = db.query(ExtractedEntity).filter(
        ExtractedEntity.id == entity_id
    ).first()

    if not entity:
        raise LookupError("Extracted entity not found.")

    document = db.query(Document).filter(
        Document.id == entity.document_id
    ).first()

    if not document:
        raise LookupError("Source document not found.")

    return _save_changes(
        db=db,
        record=entity,
        doctor=doctor,
        patient_id=document.patient_id,
        resource_type="extracted_entity",
        updates=updates,
    )


def correct_lab_result(
    db: Session,
    lab_id: int,
    doctor: User,
    updates: dict,
):
    _ensure_doctor(doctor)

    lab = db.query(LabResult).filter(
        LabResult.id == lab_id
    ).first()

    if not lab:
        raise LookupError("Lab result not found.")

    return _save_changes(
        db=db,
        record=lab,
        doctor=doctor,
        patient_id=lab.patient_id,
        resource_type="lab_result",
        updates=updates,
    )


def _review_record(
    db: Session,
    record,
    doctor: User,
    patient_id: int,
    resource_type: str,
    decision: str,
):
    _ensure_doctor(doctor)
    _ensure_pending(record)

    now = _now()

    try:
        previous_values = {
            "review_status": record.review_status,
            "needs_review": record.needs_review,
        }

        record.review_status = decision
        record.needs_review = False
        record.reviewed_by = doctor.id
        record.reviewed_at = now

        _create_audit_log(
            db=db,
            doctor=doctor,
            patient_id=patient_id,
            action=f"medical_record_{decision}",
            resource_type=resource_type,
            resource_id=record.id,
            details={
                "before": previous_values,
                "after": {
                    "review_status": decision,
                    "needs_review": False,
                    "reviewed_by": doctor.id,
                    "reviewed_at": now.isoformat(),
                },
            },
        )

        db.commit()
        db.refresh(record)

        return record

    except Exception:
        db.rollback()
        raise


def review_extracted_entity(
    db: Session,
    entity_id: int,
    doctor: User,
    decision: str,
):
    if decision not in {"approved", "rejected"}:
        raise ValueError(
            "Decision must be approved or rejected."
        )

    entity = db.query(ExtractedEntity).filter(
        ExtractedEntity.id == entity_id
    ).first()

    if not entity:
        raise LookupError("Extracted entity not found.")

    document = db.query(Document).filter(
        Document.id == entity.document_id
    ).first()

    if not document:
        raise LookupError("Source document not found.")

    return _review_record(
        db=db,
        record=entity,
        doctor=doctor,
        patient_id=document.patient_id,
        resource_type="extracted_entity",
        decision=decision,
    )


def review_lab_result(
    db: Session,
    lab_id: int,
    doctor: User,
    decision: str,
):
    if decision not in {"approved", "rejected"}:
        raise ValueError(
            "Decision must be approved or rejected."
        )

    lab = db.query(LabResult).filter(
        LabResult.id == lab_id
    ).first()

    if not lab:
        raise LookupError("Lab result not found.")

    return _review_record(
        db=db,
        record=lab,
        doctor=doctor,
        patient_id=lab.patient_id,
        resource_type="lab_result",
        decision=decision,
    )


def get_pending_reviews(
    db: Session,
    document_id: int,
    doctor: User,
):
    _ensure_doctor(doctor)

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise LookupError("Document not found.")

    entities = db.query(ExtractedEntity).filter(
        ExtractedEntity.document_id == document_id,
        ExtractedEntity.review_status == "pending",
    ).all()

    lab_results = db.query(LabResult).filter(
        LabResult.document_id == document_id,
        LabResult.review_status == "pending",
    ).all()

    return {
        "document_id": document_id,
        "patient_id": document.patient_id,
        "entities": [
            {
                "id": item.id,
                "entity_type": item.entity_type,
                "value": item.value,
                "unit": item.unit,
                "confidence": item.confidence,
                "review_status": item.review_status,
            }
            for item in entities
        ],
        "lab_results": [
            {
                "id": item.id,
                "test_name": item.test_name,
                "value": item.value,
                "unit": item.unit,
                "ref_range": item.ref_range,
                "test_date": (
                    item.test_date.isoformat()
                    if item.test_date else None
                ),
                "confidence": item.confidence,
                "review_status": item.review_status,
            }
            for item in lab_results
        ],
        "total_pending": len(entities) + len(lab_results),
    }
