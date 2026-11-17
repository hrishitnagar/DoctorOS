
from app.database.connection import SessionLocal
from app.models.audit_log import AuditLog

db = SessionLocal()

try:
    logs = (
        db.query(AuditLog)
        .filter(
            AuditLog.resource_type == "lab_result",
            AuditLog.resource_id == "3",
        )
        .order_by(AuditLog.timestamp.asc())
        .all()
    )

    print("AUDIT HISTORY FOR LAB RESULT 3")

    for log in logs:
        print("\nAction:", log.action)
        print("Doctor ID:", log.user_id)
        print("Patient ID:", log.patient_id)
        print("Timestamp:", log.timestamp)
        print("Details:", log.details)

finally:
    db.close()
