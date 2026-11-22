
from datetime import datetime, timezone
from unittest.mock import patch
from types import SimpleNamespace

import pytest

from app.models.user import User
from app.models.patient import Patient
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services import background_tasks


@pytest.fixture
def test_document(db):
    """Create an isolated synthetic document inside a rollback transaction."""

    doctor = User(
        name="Pipeline Test Doctor",
        email="pipeline-test-doctor@example.com",
        password_hash="synthetic-test-hash",
        role="doctor",
    )
    db.add(doctor)
    db.flush()

    patient = Patient(
        patient_uid="DOS-PIPELINE-TEST-001",
        name="Synthetic Pipeline Patient",
    )
    db.add(patient)
    db.flush()

    document = Document(
        patient_id=patient.id,
        document_type="test_report",
        file_path="synthetic/pipeline_test.pdf",
        uploaded_by=doctor.id,
        uploaded_at=datetime.now(timezone.utc),
        ocr_status="done",
        extraction_status="pending",
        raw_text=(
            "SYNTHETIC PIPELINE TEST DOCUMENT\n"
            "Page 1\n"
            "Synthetic laboratory report for software testing."
        ),
    )

    db.add(document)
    db.flush()

    return document


def test_pipeline_chunking(db, test_document):
    fake_extraction = SimpleNamespace(
        model_dump=lambda: {"test": "synthetic extraction"}
    )

    with patch.object(
        background_tasks,
        "process_document_ocr",
        side_effect=lambda db, document: document,
    ), patch.object(
        background_tasks,
        "extract_and_validate_medical_data",
        return_value=fake_extraction,
    ), patch.object(
        background_tasks,
        "persist_medical_extraction",
        return_value={
            "entities_saved": 0,
            "lab_results_saved": 0,
        },
    ):

        result = background_tasks.process_document_pipeline(
            db=db,
            document=test_document,
        )

    saved_count = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == test_document.id
        )
        .count()
    )

    assert result["success"] is True
    assert result["chunking"]["success"] is True
    assert result["chunking"]["chunks_created"] == saved_count
    assert saved_count > 0

