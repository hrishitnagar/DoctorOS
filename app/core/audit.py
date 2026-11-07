
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def record_audit_event(
    db: Session,
    user_id: int | None,
    action: str,
    patient_id: int | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: dict | None = None,
) -> None:
    """
    Record an audit event without storing sensitive patient details.
    """

    audit_entry = AuditLog(
        user_id=user_id,
        patient_id=patient_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        timestamp=datetime.now(timezone.utc),
    )

    db.add(audit_entry)
    db.commit()
