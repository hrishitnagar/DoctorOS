
import math

from google import genai
from google.genai import types

from app.core.config import settings


EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768

client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


def normalize_embedding(
    embedding: list[float],
) -> list[float]:
    """Normalize an embedding vector to unit length."""

    magnitude = math.sqrt(
        sum(value * value for value in embedding)
    )

    if magnitude == 0:
        raise ValueError("Cannot normalize a zero vector.")

    return [
        float(value / magnitude)
        for value in embedding
    ]


def generate_embedding(
    text: str,
    task_type: str,
) -> list[float]:
    """Generate a normalized 768-dimensional embedding."""

    if not text or not text.strip():
        raise ValueError("Cannot embed empty text.")

    allowed_tasks = {
        "RETRIEVAL_DOCUMENT",
        "RETRIEVAL_QUERY",
    }

    if task_type not in allowed_tasks:
        raise ValueError("Unsupported embedding task type.")

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=EMBEDDING_DIMENSION,
        ),
    )

    if not response.embeddings:
        raise ValueError("Google returned no embeddings.")

    embedding = response.embeddings[0].values

    if embedding is None:
        raise ValueError("Google returned an empty embedding.")

    if len(embedding) != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSION} dimensions, "
            f"received {len(embedding)}."
        )

    return normalize_embedding(embedding)


def generate_document_embedding(
    text: str,
) -> list[float]:
    """Generate an embedding for a document chunk."""

    return generate_embedding(
        text=text,
        task_type="RETRIEVAL_DOCUMENT",
    )


def generate_query_embedding(
    text: str,
) -> list[float]:
    """Generate an embedding for a user's search query."""

    return generate_embedding(
        text=text,
        task_type="RETRIEVAL_QUERY",
    )


