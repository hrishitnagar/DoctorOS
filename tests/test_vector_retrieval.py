
from app.database.connection import SessionLocal
from app.services.retrieval_service import retrieve_relevant_chunks


def test_retrieve_patient_document_chunks():
    db = SessionLocal()

    try:
        question = "What laboratory test results are recorded in this report?"

        results = retrieve_relevant_chunks(
            db=db,
            patient_id=3,
            question=question,
            top_k=5,
        )

        print("\nRETRIEVAL RESULTS:")

        for result in results:
            print({
                "chunk_id": result["chunk_id"],
                "document_id": result["document_id"],
                "patient_id": result["patient_id"],
                "page_no": result["page_no"],
                "similarity_score": result["similarity_score"],
            })

        assert len(results) > 0

        for result in results:
            assert result["patient_id"] == 3
            assert result["document_id"] == 4
            assert result["chunk_text"]

            assert 0.0 <= result["similarity_score"] <= 1.0

    finally:
        db.close()
