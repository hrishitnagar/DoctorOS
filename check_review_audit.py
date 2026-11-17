
from app.database.connection import SessionLocal
from app.models.audit_log import AuditLog

db = SessionLocal()

try:
    logs = (
        db.query(AuditLog)
        .filter(
            AuditLog.resource_type == "extracted_entity",
            AuditLog.resource_id == "7",
        )
        .order_by(AuditLog.timestamp.asc())
        .all()
    )

    print("AUDIT LOGS FOR ENTITY 7")

    for log in logs:
        print("\nAction:", log.action)
        print("Doctor ID:", log.user_id)
        print("Patient ID:", log.patient_id)
        print("Timestamp:", log.timestamp)
        print("Details:", log.details)

finally:
    db.close()
