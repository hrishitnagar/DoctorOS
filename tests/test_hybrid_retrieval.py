
from app.database.connection import SessionLocal
from app.services.hybrid_search_service import retrieve_hybrid_chunks


def test_hybrid_retrieval():

    db = SessionLocal()

    try:
        # Existing synthetic patient with a verified test document.
        patient_id = 3

        question = "laboratory"

        results = retrieve_hybrid_chunks(
            db=db,
            patient_id=patient_id,
            question=question,
            top_k=5,
            candidate_k=20,
        )

        print("\nHybrid Search Results:")

        for result in results:
            print({
                "chunk_id": result["chunk_id"],
                "document_id": result["document_id"],
                "patient_id": result["patient_id"],
                "page_no": result["page_no"],
                "similarity_score": result.get("similarity_score"),
                "keyword_score": result.get("keyword_score"),
                "vector_rank": result["vector_rank"],
                "keyword_rank": result["keyword_rank"],
                "rrf_score": result["rrf_score"],
                "chunk_text": result["chunk_text"][:200],
            })

        # At least one matching chunk should be retrieved.
        assert len(results) > 0

        # Every result must belong to the requested patient.
        assert all(
            result["patient_id"] == patient_id
            for result in results
        )

        # No duplicate chunks should appear.
        chunk_ids = [
            result["chunk_id"]
            for result in results
        ]

        assert len(chunk_ids) == len(set(chunk_ids))

        # Results must be ordered by descending RRF score.
        scores = [
            result["rrf_score"]
            for result in results
        ]

        assert scores == sorted(scores, reverse=True)

    finally:
        db.close()


if __name__ == "__main__":
    test_hybrid_retrieval()
