
from datetime import date, datetime
from typing import Any


def format_document_date(value: Any) -> str:
    """Convert document dates into readable strings."""

    if value is None:
        return "Unknown"

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    return str(value)


def build_rag_context(
    retrieved_chunks: list[dict],
) -> tuple[str, list[dict]]:
    """
    Build context and source metadata from retrieved chunks.

    Returns:
        context: Formatted text to provide to the LLM.
        sources: Metadata used for source citations.
    """

    if not retrieved_chunks:
        return "", []

    context_sections = []
    sources = []

    for index, chunk in enumerate(retrieved_chunks, start=1):

        source_id = f"S{index}"

        chunk_text = chunk.get("chunk_text")

        if not isinstance(chunk_text, str) or not chunk_text.strip():
            continue

        source = {
            "source_id": source_id,
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],
            "patient_id": chunk["patient_id"],
            "chunk_index": chunk["chunk_index"],
            "page_no": chunk.get("page_no"),
            "document_date": format_document_date(
                chunk.get("document_date")
            ),
        }

        context_section = (
            f"[{source_id}]\n"
            f"Document ID: {source['document_id']}\n"
            f"Page Number: {source['page_no'] or 'Unknown'}\n"
            f"Document Date: {source['document_date']}\n"
            f"Content:\n{chunk_text.strip()}"
        )

        context_sections.append(context_section)
        sources.append(source)

    context = "\n\n---\n\n".join(context_sections)

    return context, sources
