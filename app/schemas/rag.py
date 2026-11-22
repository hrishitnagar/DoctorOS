
from pydantic import BaseModel, Field


class RAGAskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Question about the patient's medical documents",
        examples=[
            "What laboratory results are recorded in the latest report?"
        ],
    )


class RAGCitation(BaseModel):
    source_id: str
    chunk_id: int
    document_id: int
    patient_id: int
    chunk_index: int
    page_no: int | None = None
    document_date: str


class RAGAskResponse(BaseModel):
    answer: str
    citations: list[RAGCitation]
    retrieved_chunks: int
