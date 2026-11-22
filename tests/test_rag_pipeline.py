
import pytest

from app.services import rag_pipeline_service
from app.services.rag_pipeline_service import (
    run_rag_pipeline,
    RAGPipelineError,
)


@pytest.fixture
def sample_chunks():
    return [
        {
            "chunk_id": 101,
            "document_id": 10,
            "patient_id": 5,
            "chunk_index": 0,
            "chunk_text": "Haemoglobin: 12.5 g/dL",
            "page_no": 2,
            "document_date": "2026-10-15",
            "rrf_score": 0.032,
        },
        {
            "chunk_id": 102,
            "document_id": 10,
            "patient_id": 5,
            "chunk_index": 1,
            "chunk_text": "WBC count: 7500 cells/mcL",
            "page_no": 3,
            "document_date": "2026-10-15",
            "rrf_score": 0.029,
        },
    ]


def test_rag_pipeline_success(monkeypatch, sample_chunks):

    def mock_retrieval(**kwargs):
        assert kwargs["patient_id"] == 5
        return sample_chunks

    def mock_generation(question, context):
        assert "Haemoglobin: 12.5 g/dL" in context
        assert "WBC count: 7500 cells/mcL" in context

        return (
            "Haemoglobin is 12.5 g/dL [S1]. "
            "WBC count is 7500 cells/mcL [S2]."
        )

    monkeypatch.setattr(
        rag_pipeline_service,
        "retrieve_hybrid_chunks",
        mock_retrieval,
    )

    monkeypatch.setattr(
        rag_pipeline_service,
        "generate_rag_answer",
        mock_generation,
    )

    result = run_rag_pipeline(
        db=None,
        patient_id=5,
        question="What are the recorded laboratory values?",
    )

    assert result["retrieved_chunks"] == 2
    assert len(result["citations"]) == 2
    assert result["citations"][0]["source_id"] == "S1"
    assert result["citations"][1]["source_id"] == "S2"


def test_rag_pipeline_handles_no_retrieved_chunks(monkeypatch):

    monkeypatch.setattr(
        rag_pipeline_service,
        "retrieve_hybrid_chunks",
        lambda **kwargs: [],
    )

    result = run_rag_pipeline(
        db=None,
        patient_id=5,
        question="What is the haemoglobin level?",
    )

    assert result["retrieved_chunks"] == 0
    assert result["citations"] == []
    assert "could not find relevant information" in (
        result["answer"].lower()
    )


def test_rag_pipeline_rejects_cross_patient_chunk(
    monkeypatch,
    sample_chunks,
):

    sample_chunks[0]["patient_id"] = 99

    monkeypatch.setattr(
        rag_pipeline_service,
        "retrieve_hybrid_chunks",
        lambda **kwargs: sample_chunks,
    )

    generation_called = False

    def mock_generation(question, context):
        nonlocal generation_called
        generation_called = True
        return "Unexpected answer."

    monkeypatch.setattr(
        rag_pipeline_service,
        "generate_rag_answer",
        mock_generation,
    )

    with pytest.raises(
        RAGPipelineError,
        match="does not belong to the requested patient",
    ):
        run_rag_pipeline(
            db=None,
            patient_id=5,
            question="What are the laboratory results?",
        )

    assert generation_called is False


def test_rag_pipeline_rejects_invalid_citation(
    monkeypatch,
    sample_chunks,
):

    monkeypatch.setattr(
        rag_pipeline_service,
        "retrieve_hybrid_chunks",
        lambda **kwargs: sample_chunks,
    )

    monkeypatch.setattr(
        rag_pipeline_service,
        "generate_rag_answer",
        lambda **kwargs: "Haemoglobin is 12.5 g/dL [S9].",
    )

    from app.services.citation_service import CitationValidationError

    with pytest.raises(CitationValidationError):
        run_rag_pipeline(
            db=None,
            patient_id=5,
            question="What is the haemoglobin level?",
        )


def test_rag_pipeline_rejects_invalid_patient_id():

    with pytest.raises(ValueError, match="Invalid patient ID"):
        run_rag_pipeline(
            db=None,
            patient_id=0,
            question="What is the haemoglobin level?",
        )


def test_rag_pipeline_rejects_empty_question():

    with pytest.raises(ValueError, match="Question cannot be empty"):
        run_rag_pipeline(
            db=None,
            patient_id=5,
            question="   ",
        )
