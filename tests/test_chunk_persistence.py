
from app.database.connection import SessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.chunking_service import create_document_chunks

db = SessionLocal()

try:
    # Load only the synthetic test document.
    document = (
        db.query(Document)
        .filter(Document.id == 4)
        .first()
    )

    if document is None:
        print("Document ID 4 not found.")
    else:
        print("Document ID:", document.id)
        print("Patient ID:", document.patient_id)
        print("OCR status:", document.ocr_status)

        # Generate and save chunks.
        total_chunks = create_document_chunks(db, document)

        print("\nChunks created:", total_chunks)

        # Read saved chunks back from PostgreSQL.
        saved_chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document.id)
            .order_by(DocumentChunk.chunk_index)
            .all()
        )

        print("\nSAVED CHUNK DETAILS")

        for chunk in saved_chunks:
            print(
                f"Index: {chunk.chunk_index} | "
                f"Page: {chunk.page_no} | "
                f"Tokens: {len(__import__('tiktoken').get_encoding('cl100k_base').encode(chunk.chunk_text))} | "
                f"Embedding: {chunk.embedding}"
            )

        # Verify database records.
        assert len(saved_chunks) == total_chunks
        assert all(
            chunk.patient_id == document.patient_id
            for chunk in saved_chunks
        )
        assert all(
            chunk.embedding is None
            for chunk in saved_chunks
        )
        assert all(
            chunk.page_no is not None
            for chunk in saved_chunks
        )

        print("\nDATABASE PERSISTENCE TEST PASSED")

finally:
    db.close()
