
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import (
    generate_query_embedding,
    EMBEDDING_DIMENSION,
)


def retrieve_relevant_chunks(
    db: Session,
    patient_id: int,
    question: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Retrieve relevant document chunks for an authorized patient
    using Gemini query embeddings and pgvector cosine distance.

    IMPORTANT:
    The caller must authorize the doctor-patient relationship
    before calling this function.
    """

    # 1. Validate inputs.
    if patient_id <= 0:
        raise ValueError("Invalid patient ID.")

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not isinstance(top_k, int) or isinstance(top_k, bool):
        raise ValueError("top_k must be an integer.")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20.")

    # 2. Generate the query embedding.
    query_embedding = generate_query_embedding(
        question.strip()
    )

    # 3. Verify embedding dimensions.
    if len(query_embedding) != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSION} dimensions, "
            f"received {len(query_embedding)}."
        )

    # 4. Calculate cosine distance.
    cosine_distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    ).label("cosine_distance")

    # 5. Search only within the authorized patient's chunks.
    results = (
        db.query(
            DocumentChunk.id,
            DocumentChunk.document_id,
            DocumentChunk.patient_id,
            DocumentChunk.chunk_index,
            DocumentChunk.chunk_text,
            DocumentChunk.page_no,
            DocumentChunk.document_date,
            cosine_distance,
        )
        .filter(
            DocumentChunk.patient_id == patient_id,
            DocumentChunk.embedding.is_not(None),
        )
        .order_by(cosine_distance.asc())
        .limit(top_k)
        .all()
    )

    # 6. Format the retrieved results.
    retrieved_chunks = []

    for row in results:
        distance = float(row.cosine_distance)

        similarity = max(
            0.0,
            min(1.0, 1.0 - distance)
        )

        retrieved_chunks.append({
            "chunk_id": row.id,
            "document_id": row.document_id,
            "patient_id": row.patient_id,
            "chunk_index": row.chunk_index,
            "chunk_text": row.chunk_text,
            "page_no": row.page_no,
            "document_date": row.document_date,
            "similarity_score": similarity,
        })

    return retrieved_chunks
