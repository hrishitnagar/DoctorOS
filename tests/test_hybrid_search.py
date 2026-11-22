
import pytest

from app.services.hybrid_search_service import reciprocal_rank_fusion


def test_rrf_combines_vector_and_keyword_results():

    vector_results = [
        {"chunk_id": 1, "chunk_text": "Chunk A", "similarity_score": 0.95},
        {"chunk_id": 2, "chunk_text": "Chunk B", "similarity_score": 0.90},
        {"chunk_id": 3, "chunk_text": "Chunk C", "similarity_score": 0.85},
    ]

    keyword_results = [
        {"chunk_id": 2, "chunk_text": "Chunk B", "keyword_score": 0.8},
        {"chunk_id": 3, "chunk_text": "Chunk C", "keyword_score": 0.7},
        {"chunk_id": 1, "chunk_text": "Chunk A", "keyword_score": 0.6},
    ]

    results = reciprocal_rank_fusion(
        vector_results=vector_results,
        keyword_results=keyword_results,
        k=60,
    )

    # All three unique chunks should be present.
    assert len(results) == 3

    # Chunk 2 ranks second in vector search and first in keyword search.
    assert results[0]["chunk_id"] == 2

    # Check the RRF score.
    expected_score = (1 / 62) + (1 / 61)

    assert results[0]["rrf_score"] == pytest.approx(expected_score)

    # Both rankings should be preserved.
    assert results[0]["vector_rank"] == 2
    assert results[0]["keyword_rank"] == 1

    print("\nRRF Results:")

    for result in results:
        print({
            "chunk_id": result["chunk_id"],
            "vector_rank": result["vector_rank"],
            "keyword_rank": result["keyword_rank"],
            "rrf_score": round(result["rrf_score"], 6),
        })


def test_rrf_handles_chunks_found_in_only_one_search():

    vector_results = [
        {"chunk_id": 10, "chunk_text": "Vector-only chunk"}
    ]

    keyword_results = [
        {"chunk_id": 20, "chunk_text": "Keyword-only chunk"}
    ]

    results = reciprocal_rank_fusion(
        vector_results,
        keyword_results,
    )

    assert len(results) == 2

    assert results[0]["rrf_score"] == pytest.approx(1 / 61)
    assert results[1]["rrf_score"] == pytest.approx(1 / 61)


def test_rrf_rejects_invalid_constant():

    with pytest.raises(ValueError):
        reciprocal_rank_fusion([], [], k=0)
