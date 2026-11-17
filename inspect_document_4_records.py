
from app.database.connection import SessionLocal
from app.models.lab_result import LabResult

db = SessionLocal()

# Only these three incorrectly extracted synthetic identifiers.
incorrect_names = [
    "TEST-DOCTOROS",
    "SYN-SPEC",
    "SYN-REPORT",
]

try:
    records = (
        db.query(LabResult)
        .filter(
            LabResult.document_id == 4,
            LabResult.patient_id == 3,
            LabResult.test_name.in_(incorrect_names),
        )
        .all()
    )

    print("Records selected for cleanup:")

    for record in records:
        print(
            f"ID: {record.id} | "
            f"Name: {record.test_name} | "
            f"Value: {record.value} | "
            f"Document: {record.document_id}"
        )

    if not records:
        print("No matching incorrect records found.")
    else:
        confirmation = input(
            "\nType DELETE to remove only these records: "
        )

        if confirmation == "DELETE":
            for record in records:
                db.delete(record)

            db.commit()
            print(f"\nDeleted {len(records)} incorrect records.")
        else:
            print("\nCleanup cancelled. No records were deleted.")

except Exception:
    db.rollback()
    raise

finally:
    db.close()
