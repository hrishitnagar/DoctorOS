
from app.services.chunking_service import (
    TOKENIZER,
    split_text_into_chunks,
    split_document_into_page_chunks,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


# Test 1: Token-based chunking
sample_text = " ".join(
    ["This is synthetic medical test text for software testing."] * 150
)

chunks = split_text_into_chunks(sample_text)

print("TEST 1: TOKEN CHUNKING")
print("Total chunks:", len(chunks))

for index, chunk in enumerate(chunks):
    token_count = len(TOKENIZER.encode(chunk))
    print(f"Chunk {index}: {token_count} tokens")

assert len(chunks) > 1
assert all(
    len(TOKENIZER.encode(chunk)) <= CHUNK_SIZE
    for chunk in chunks
)

print("Token chunking test passed!")


# Test 2: Page-number preservation
page_aware_text = (
    "SYNTHETIC PAGE ONE CONTENT. " * 100
    + "\n\f\n"
    + "SYNTHETIC PAGE TWO CONTENT. " * 100
)

page_chunks = split_document_into_page_chunks(page_aware_text)

page_numbers = sorted(set(
    chunk["page_no"] for chunk in page_chunks
))

print("\nTEST 2: PAGE PRESERVATION")
print("Total page chunks:", len(page_chunks))
print("Page numbers found:", page_numbers)

assert page_numbers == [1, 2]
assert all(
    chunk["chunk_text"].strip()
    for chunk in page_chunks
)

print("Page preservation test passed!")


# Test 3: Sequential chunk indexes
indexes = [chunk["chunk_index"] for chunk in page_chunks]

assert indexes == list(range(len(page_chunks)))

print("\nTEST 3: CHUNK INDEX")
print("Chunk indexes:", indexes)
print("Sequential index test passed!")

print("\nALL CHUNKING TESTS PASSED")
