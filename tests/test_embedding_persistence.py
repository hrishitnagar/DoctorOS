
from app.database.connection import SessionLocal
from app.models.document_chunk import DocumentChunk
from app.services.embedding_persistence_service import (
    generate_document_embeddings,
)

db = SessionLocal()

try:
    document_id = 4

    print("Generating embeddings for Document:", document_id)

    result = generate_document_embeddings(
        db=db,
        document_id=document_id,
    )

    print("\nEMBEDDING RESULT")
    print(result)

    # Verify the saved database records.
    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )

    print("\nDATABASE VERIFICATION")

    for chunk in chunks:
        print("Chunk ID:", chunk.id)
        print("Page:", chunk.page_no)
        print(
            "Embedding dimensions:",
            len(chunk.embedding) if chunk.embedding else 0
        )

        assert chunk.embedding is not None
        assert len(chunk.embedding) == 768

    assert len(chunks) > 0

    print("\nEMBEDDING DATABASE TEST PASSED")

finally:
    db.close()
