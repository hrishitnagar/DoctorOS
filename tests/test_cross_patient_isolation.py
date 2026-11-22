

from datetime import datetime, timezone

import pytest
from app.models.user import User
from app.models.patient import Patient
from app.models.document import Document
from app.models.document_chunk import DocumentChunk





def make_test_embedding(index: int) -> list[float]:
    """Create a deterministic 768-dimensional unit vector."""
    embedding = [0.0] * 768
    embedding[index] = 1.0
    return embedding


def test_cross_patient_retrieval_isolation(db, monkeypatch):
    from app.services.retrieval_service import retrieve_relevant_chunks

    # 1. Create a synthetic doctor.
    doctor = User(
        name="Isolation Test Doctor",
        email="isolation-test-doctor@example.com",
        password_hash="synthetic-test-hash",
        role="doctor",
    )

    db.add(doctor)
    db.flush()

    # 2. Create two separate synthetic patients.
    patient_a = Patient(
        patient_uid="DOS-AUTH-ISOLATION-A",
        name="Synthetic Patient A",
    )

    patient_b = Patient(
        patient_uid="DOS-AUTH-ISOLATION-B",
        name="Synthetic Patient B",
    )

    db.add_all([patient_a, patient_b])
    db.flush()

    # 3. Create one document for each patient.
    document_a = Document(
        patient_id=patient_a.id,
        document_type="test_report",
        file_path="synthetic/isolation_test_a.pdf",
        uploaded_by=doctor.id,
        uploaded_at=datetime.now(timezone.utc),
        ocr_status="done",
        extraction_status="done",
        raw_text="Synthetic report belonging to Patient A.",
    )

    document_b = Document(
        patient_id=patient_b.id,
        document_type="test_report",
        file_path="synthetic/isolation_test_b.pdf",
        uploaded_by=doctor.id,
        uploaded_at=datetime.now(timezone.utc),
        ocr_status="done",
        extraction_status="done",
        raw_text="Synthetic report belonging to Patient B.",
    )

    db.add_all([document_a, document_b])
    db.flush()

    # 4. Create separate embeddings and chunks.
    embedding_a = make_test_embedding(0)
    embedding_b = make_test_embedding(1)

    chunk_a = DocumentChunk(
        document_id=document_a.id,
        patient_id=patient_a.id,
        chunk_index=0,
        chunk_text="Synthetic medical information for Patient A.",
        embedding=embedding_a,
        page_no=1,
    )

    chunk_b = DocumentChunk(
        document_id=document_b.id,
        patient_id=patient_b.id,
        chunk_index=0,
        chunk_text="Synthetic medical information for Patient B.",
        embedding=embedding_b,
        page_no=1,
    )

    db.add_all([chunk_a, chunk_b])
    db.flush()

    # 5. Mock the embedding generator so this test does not
    # need to make an external Gemini API request.
    def fake_query_embedding(question: str) -> list[float]:
        if question == "question for patient A":
            return embedding_a

        if question == "question for patient B":
            return embedding_b

        raise ValueError("Unexpected test question.")

    monkeypatch.setattr(
        "app.services.retrieval_service.generate_query_embedding",
        fake_query_embedding,
    )

    # 6. Retrieve Patient A's chunks.
    results_a = retrieve_relevant_chunks(
        db=db,
        patient_id=patient_a.id,
        question="question for patient A",
        top_k=5,
    )

    assert len(results_a) == 1
    assert results_a[0]["patient_id"] == patient_a.id
    assert results_a[0]["document_id"] == document_a.id
    assert results_a[0]["chunk_id"] == chunk_a.id
    assert results_a[0]["similarity_score"] == pytest.approx(1.0)

    # Explicitly verify Patient B's chunk was not returned.
    assert all(
        result["patient_id"] != patient_b.id
        for result in results_a
    )

    # 7. Retrieve Patient B's chunks.
    results_b = retrieve_relevant_chunks(
        db=db,
        patient_id=patient_b.id,
        question="question for patient B",
        top_k=5,
    )

    assert len(results_b) == 1
    assert results_b[0]["patient_id"] == patient_b.id
    assert results_b[0]["document_id"] == document_b.id
    assert results_b[0]["chunk_id"] == chunk_b.id
    assert results_b[0]["similarity_score"] == pytest.approx(1.0)

    # Explicitly verify Patient A's chunk was not returned.
    assert all(
        result["patient_id"] != patient_a.id
        for result in results_b
    )
