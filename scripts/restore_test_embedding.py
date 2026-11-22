
from app.database.connection import SessionLocal
from app.models.document_chunk import DocumentChunk
from app.services.embedding_persistence_service import (
    generate_document_embedding,
    EMBEDDING_DIMENSION,
)


def restore_test_embedding():
    db = SessionLocal()

    try:
        # Fetch only the affected synthetic test chunk.
        chunk = db.get(DocumentChunk, 16)

        if chunk is None:
            raise ValueError("Test chunk ID 8 does not exist.")

        if chunk.patient_id != 3 or chunk.document_id != 4:
            raise ValueError("Chunk ownership does not match expected test data.")

        if not chunk.chunk_text.startswith("SYNTHETIC TEST DOCUMENT"):
            raise ValueError(
                "This is not the expected synthetic test document. "
                "No changes made."
            )

        if chunk.embedding is not None:
            print("Chunk already has an embedding. No changes needed.")
            return

        # Generate a document embedding.
        embedding = generate_document_embedding(chunk.chunk_text)

        if len(embedding) != EMBEDDING_DIMENSION:
            raise ValueError("Unexpected embedding dimensions.")

        # Update the existing chunk without recreating it.
        chunk.embedding = embedding

        db.commit()
        db.refresh(chunk)

        print("Synthetic test embedding restored successfully.")
        print("Chunk ID:", chunk.id)
        print("Patient ID:", chunk.patient_id)
        print("Embedding dimensions:", len(chunk.embedding))

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    restore_test_embedding()
