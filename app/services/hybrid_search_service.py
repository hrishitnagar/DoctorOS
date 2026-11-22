

from sqlalchemy.orm import Session

from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.keyword_search_service import retrieve_keyword_chunks


def reciprocal_rank_fusion(
    vector_results: list[dict],
    keyword_results: list[dict],
    k: int = 60,
) -> list[dict]:
    """
    Combine vector and keyword rankings using RRF.
    """

    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        raise ValueError("k must be a positive integer.")

    combined = {}

    # Process vector search results.
    for rank, result in enumerate(vector_results, start=1):
        chunk_id = result["chunk_id"]

        if chunk_id not in combined:
            combined[chunk_id] = {
                **result,
                "rrf_score": 0.0,
                "vector_rank": None,
                "keyword_rank": None,
            }

        combined[chunk_id]["rrf_score"] += 1 / (k + rank)
        combined[chunk_id]["vector_rank"] = rank

    # Process ALL keyword search results.
    for rank, result in enumerate(keyword_results, start=1):
        chunk_id = result["chunk_id"]

        if chunk_id not in combined:
            combined[chunk_id] = {
                **result,
                "rrf_score": 0.0,
                "vector_rank": None,
                "keyword_rank": None,
            }
        else:
            # Preserve vector metadata and add keyword metadata.
            combined[chunk_id].update({
                key: value
                for key, value in result.items()
                if key not in (
                    "rrf_score",
                    "vector_rank",
                    "keyword_rank",
                )
            })

        combined[chunk_id]["rrf_score"] += 1 / (k + rank)
        combined[chunk_id]["keyword_rank"] = rank

    return sorted(
        combined.values(),
        key=lambda item: item["rrf_score"],
        reverse=True,
    )


def retrieve_hybrid_chunks(
    db: Session,
    patient_id: int,
    question: str,
    top_k: int = 5,
    candidate_k: int = 20,
) -> list[dict]:
    """
    Retrieve patient-specific chunks using vector and keyword search,
    then combine their rankings using Reciprocal Rank Fusion.

    The caller must authorize the doctor-patient relationship
    before calling this function.
    """

    if (
        not isinstance(patient_id, int)
        or isinstance(patient_id, bool)
        or patient_id <= 0
    ):
        raise ValueError("Invalid patient ID.")

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not isinstance(top_k, int) or isinstance(top_k, bool):
        raise ValueError("top_k must be an integer.")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20.")

    if not isinstance(candidate_k, int) or isinstance(candidate_k, bool):
        raise ValueError("candidate_k must be an integer.")

    if not top_k <= candidate_k <= 20:
        raise ValueError(
            "candidate_k must be between top_k and 20."
        )

    vector_results = retrieve_relevant_chunks(
        db=db,
        patient_id=patient_id,
        question=question.strip(),
        top_k=candidate_k,
    )

    keyword_results = retrieve_keyword_chunks(
        db=db,
        patient_id=patient_id,
        question=question.strip(),
        top_k=candidate_k,
    )

    fused_results = reciprocal_rank_fusion(
        vector_results=vector_results,
        keyword_results=keyword_results,
        k=60,
    )

    return fused_results[:top_k]
