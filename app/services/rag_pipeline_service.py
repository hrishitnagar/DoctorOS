
from sqlalchemy.orm import Session

from app.services.hybrid_search_service import retrieve_hybrid_chunks
from app.services.context_builder import build_rag_context
from app.services.rag_generation_service import generate_rag_answer
from app.services.citation_service import validate_citations


class RAGPipelineError(Exception):
    """Raised when the RAG pipeline encounters an integrity problem."""


def run_rag_pipeline(
    db: Session,
    patient_id: int,
    question: str,
    top_k: int = 5,
    candidate_k: int = 20,
) -> dict:
    """
    Run the complete patient-specific RAG pipeline.

    Steps:
        1. Retrieve relevant chunks using hybrid search.
        2. Verify patient ownership of retrieved chunks.
        3. Build context and source metadata.
        4. Generate an answer using Gemini.
        5. Validate generated citations.

    The caller must authorize the doctor-patient relationship
    before calling this function.

    Returns:
        A dictionary containing the answer, validated citations,
        and retrieved chunk count.
    """

    # 1. Validate patient ID.
    if (
        not isinstance(patient_id, int)
        or isinstance(patient_id, bool)
        or patient_id <= 0
    ):
        raise ValueError("Invalid patient ID.")

    # 2. Validate the question.
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question cannot be empty.")

    # 3. Retrieve relevant patient-specific chunks.
    retrieved_chunks = retrieve_hybrid_chunks(
        db=db,
        patient_id=patient_id,
        question=question.strip(),
        top_k=top_k,
        candidate_k=candidate_k,
    )

    # 4. Verify that every retrieved chunk belongs to this patient.
    for chunk in retrieved_chunks:
        if chunk.get("patient_id") != patient_id:
            raise RAGPipelineError(
                "Retrieved chunk does not belong to the requested patient."
            )

    # 5. Build context and source metadata.
    context, sources = build_rag_context(retrieved_chunks)

    # 6. Verify source ownership before generation.
    for source in sources:
        if source.get("patient_id") != patient_id:
            raise RAGPipelineError(
                "Source metadata does not belong to the requested patient."
            )

    # 7. Generate the answer using Gemini.
    answer = generate_rag_answer(
        question=question.strip(),
        context=context,
    )

    # 8. Validate citations against retrieved source metadata.
    # If no sources were retrieved, a citation-free response is expected.
    validated_citations = validate_citations(
        answer=answer,
        sources=sources,
        require_citations=bool(sources),
    )

    # 9. Return the final RAG response.
    return {
        "answer": answer,
        "citations": validated_citations,
        "retrieved_chunks": len(retrieved_chunks),
    }
