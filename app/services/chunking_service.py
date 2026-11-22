
from datetime import date
import tiktoken

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk


# Chunking configuration
CHUNK_SIZE = 400
CHUNK_OVERLAP = 100

TOKENIZER = tiktoken.get_encoding("cl100k_base")


def split_text_into_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:

    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid overlap value")

    tokens = TOKENIZER.encode(text)

    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))

        chunk_tokens = tokens[start:end]
        chunk_text = TOKENIZER.decode(chunk_tokens).strip()

        if chunk_text:
            chunks.append(chunk_text)

        if end == len(tokens):
            break

        start += step

    return chunks


def split_document_into_page_chunks(
    raw_text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict]:

    if not raw_text or not raw_text.strip():
        return []

    pages = raw_text.split("\f")
    document_chunks = []

    chunk_index = 0

    for page_number, page_text in enumerate(pages, start=1):

        page_text = page_text.strip()

        if not page_text:
            continue

        page_chunks = split_text_into_chunks(
            page_text,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk_text in page_chunks:
            document_chunks.append({
                "chunk_index": chunk_index,
                "page_no": page_number,
                "chunk_text": chunk_text,
            })

            chunk_index += 1

    return document_chunks


def create_document_chunks(
    db: Session,
    document: Document,
) -> int:
    """
    Generate and persist page-aware chunks for one document.

    Existing chunks for this document are replaced in the
    same transaction. Embeddings remain NULL for Stage 6.1.
    """

    if not document.raw_text or not document.raw_text.strip():
        raise ValueError("Document has no OCR text to chunk")

    if document.uploaded_at is None:
        raise ValueError("Document upload date is missing")

    chunks = split_document_into_page_chunks(document.raw_text)

    if not chunks:
        raise ValueError("No chunks could be generated")

    upload_date = document.uploaded_at.date()

    try:
        # Remove previous chunks for this document.
        db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document.id
        ).delete(synchronize_session=False)

        # Prepare new chunk records.
        records = [
            DocumentChunk(
                document_id=document.id,
                patient_id=document.patient_id,
                chunk_index=chunk["chunk_index"],
                chunk_text=chunk["chunk_text"],
                page_no=chunk["page_no"],
                document_date=upload_date,
                embedding=None,
            )
            for chunk in chunks
        ]

        db.add_all(records)
        db.flush()

        # Commit deletion and insertion together.
        db.commit()

        return len(records)

    except Exception:
        db.rollback()
        raise

