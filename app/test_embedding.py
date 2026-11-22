
import math

from app.services.embedding_service import (
    generate_document_embedding,
    EMBEDDING_DIMENSION,
)


# Synthetic text only — not a real patient record.
sample_text = """
SYNTHETIC MEDICAL TEST REPORT.
Test name: Hemoglobin.
Test value: 11.2 g/dL.
This is fictional data for software testing only.
"""


print("Generating Gemini embedding...")

embedding = generate_document_embedding(sample_text)

# Verify vector dimensions
print("\nEmbedding dimensions:", len(embedding))

assert len(embedding) == EMBEDDING_DIMENSION

# Verify all values are valid
assert all(math.isfinite(value) for value in embedding)

# Verify normalization
magnitude = math.sqrt(
    sum(value * value for value in embedding)
)

print("Vector magnitude:", magnitude)

assert abs(magnitude - 1.0) < 1e-5

print("\nGEMINI EMBEDDING TEST PASSED")
