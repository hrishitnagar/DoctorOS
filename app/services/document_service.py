
import uuid
from pathlib import Path
from datetime import datetime, timezone

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.patient import Patient


UPLOAD_DIR = Path("uploads/documents")

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


async def create_document(
    db: Session,
    patient_id: int,
    uploaded_by: int,
    file: UploadFile,
) -> Document:

    original_filename = file.filename or "uploaded_file"
    file_extension = Path(original_filename).suffix.lower()

    # Validate file extension
    if file_extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type. Allowed: PDF, PNG, JPG, JPEG."
        )

    # Read uploaded content
    file_contents = await file.read()

    # Validate file size
    if len(file_contents) > MAX_FILE_SIZE:
        raise ValueError("File size cannot exceed 10 MB.")

    if not file_contents:
        raise ValueError("Uploaded file is empty.")

    # Check that patient exists
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if not patient:
        raise ValueError("Patient not found.")

    # Generate UUID filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # Create upload directory
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Save uploaded file
    file_path = UPLOAD_DIR / unique_filename

    with file_path.open("wb") as buffer:
        buffer.write(file_contents)

    # Create database record using actual model fields
    document = Document(
        patient_id=patient_id,
        document_type=file_extension.lstrip(".").upper(),
        file_path=str(file_path),
        uploaded_by=uploaded_by,
        ocr_status="pending",
        uploaded_at=datetime.now(timezone.utc),
    )

    try:
        db.add(document)
        db.commit()
        db.refresh(document)

    except Exception:
        db.rollback()

        # Remove file if database insertion fails
        if file_path.exists():
            file_path.unlink()

        raise

    return document
