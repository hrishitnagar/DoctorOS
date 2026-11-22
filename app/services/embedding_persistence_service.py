
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk

from app.services.embedding_service import (
    generate_document_embedding,
    EMBEDDING_DIMENSION,
)


def generate_document_embeddings(
    db: Session,
    document_id: int,
) -> dict:
    """
    Generate and store embeddings for chunks belonging
    to one document.

    Existing embeddings are skipped.
    """

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise ValueError(
            f"Document {document_id} not found."
        )

    chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document_id,
            DocumentChunk.patient_id == document.patient_id,
            DocumentChunk.embedding.is_(None),
        )
        .order_by(DocumentChunk.chunk_index)
        .all()
    )

    if not chunks:
        existing_count = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id == document_id,
                DocumentChunk.patient_id == document.patient_id,
            )
            .count()
        )

        return {
            "document_id": document_id,
            "embeddings_created": 0,
            "already_processed": existing_count,
            "message": "No chunks require embedding generation.",
        }

    created_count = 0

    try:
        for chunk in chunks:

            embedding = generate_document_embedding(
                chunk.chunk_text
            )

            if len(embedding) != EMBEDDING_DIMENSION:
                raise ValueError(
                    f"Invalid embedding dimension for chunk "
                    f"{chunk.id}."
                )

            chunk.embedding = embedding
            created_count += 1

        # Save all embeddings together.
        db.commit()

        return {
            "document_id": document_id,
            "embeddings_created": created_count,
            "already_processed": 0,
            "message": "Document embeddings saved successfully.",
        }

    except Exception:
        db.rollback()
        raise
