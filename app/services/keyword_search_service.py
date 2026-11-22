
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk


def retrieve_keyword_chunks(
    db: Session,
    patient_id: int,
    question: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Retrieve relevant document chunks using PostgreSQL
    full-text keyword search.

    The caller must authorize the doctor-patient relationship
    before calling this function.
    """

    # 1. Validate inputs.
    if not isinstance(patient_id, int) or isinstance(patient_id, bool) or patient_id <= 0:
        raise ValueError("Invalid patient ID.")

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not isinstance(top_k, int) or isinstance(top_k, bool):
        raise ValueError("top_k must be an integer.")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20.")

    # 2. Convert document text into searchable tokens.
    document_vector = func.to_tsvector(
        "simple",
        DocumentChunk.chunk_text
    )

    # 3. Convert the doctor's question into a PostgreSQL search query.
    search_query = func.websearch_to_tsquery(
        "simple",
        question.strip()
    )

    # 4. Calculate keyword relevance.
    keyword_score = func.ts_rank_cd(
        document_vector,
        search_query
    ).label("keyword_score")

    # 5. Retrieve matching chunks belonging only to this patient.
    results = (
        db.query(
            DocumentChunk.id,
            DocumentChunk.document_id,
            DocumentChunk.patient_id,
            DocumentChunk.chunk_index,
            DocumentChunk.chunk_text,
            DocumentChunk.page_no,
            DocumentChunk.document_date,
            keyword_score,
        )
        .filter(
            DocumentChunk.patient_id == patient_id,
            document_vector.op("@@")(search_query),
        )
        .order_by(keyword_score.desc())
        .limit(top_k)
        .all()
    )

    # 6. Format results.
    retrieved_chunks = []

    for row in results:
        retrieved_chunks.append({
            "chunk_id": row.id,
            "document_id": row.document_id,
            "patient_id": row.patient_id,
            "chunk_index": row.chunk_index,
            "chunk_text": row.chunk_text,
            "page_no": row.page_no,
            "document_date": row.document_date,
            "keyword_score": float(row.keyword_score),
        })

    return retrieved_chunks
