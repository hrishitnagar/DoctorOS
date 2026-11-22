
from app.services.context_builder import build_rag_context


def test_build_rag_context():

    retrieved_chunks = [
        {
            "chunk_id": 101,
            "document_id": 10,
            "patient_id": 5,
            "chunk_index": 0,
            "chunk_text": "Haemoglobin: 12.5 g/dL",
            "page_no": 2,
            "document_date": None,
            "rrf_score": 0.032,
        },
        {
            "chunk_id": 102,
            "document_id": 10,
            "patient_id": 5,
            "chunk_index": 1,
            "chunk_text": "WBC count: 7500 cells/mcL",
            "page_no": 3,
            "document_date": None,
            "rrf_score": 0.029,
        },
    ]

    context, sources = build_rag_context(retrieved_chunks)

    assert "[S1]" in context
    assert "[S2]" in context

    assert "Haemoglobin: 12.5 g/dL" in context
    assert "WBC count: 7500 cells/mcL" in context

    assert len(sources) == 2

    assert sources[0]["document_id"] == 10
    assert sources[0]["page_no"] == 2

    assert sources[1]["page_no"] == 3


def test_build_rag_context_empty():

    context, sources = build_rag_context([])

    assert context == ""
    assert sources == []
