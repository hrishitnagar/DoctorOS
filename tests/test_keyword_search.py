
from app.database.connection import SessionLocal
from app.services.keyword_search_service import retrieve_keyword_chunks


def test_keyword_search():
    db = SessionLocal()

    try:
        # Use the synthetic patient that already has a test document.
        patient_id = 3

        question = "laboratory"

        results = retrieve_keyword_chunks(
            db=db,
            patient_id=patient_id,
            question=question,
            top_k=5,
        )

        print("\nKeyword Search Results:")

        for result in results:
            print({
                "chunk_id": result["chunk_id"],
                "document_id": result["document_id"],
                "patient_id": result["patient_id"],
                "page_no": result["page_no"],
                "keyword_score": result["keyword_score"],
                "chunk_text": result["chunk_text"][:200],
            })

        # Every returned chunk must belong to the requested patient.
        assert all(
            result["patient_id"] == patient_id
            for result in results
        )

        # Our existing synthetic report should match this query.
        assert len(results) > 0

    finally:
        db.close()


if __name__ == "__main__":
    test_keyword_search()
