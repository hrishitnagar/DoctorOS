
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.rag import RAGCitation


# -----------------------------------------
# 1. Chat Request
# -----------------------------------------

class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Doctor's question about the patient's medical records",
    )

    conversation_id: int | None = Field(
        default=None,
        gt=0,
        description="Existing conversation ID for follow-up questions",
    )


# -----------------------------------------
# 2. Chat Message
# -----------------------------------------

class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: Literal["user", "assistant"]
    content: str
    citations: list[RAGCitation] = Field(default_factory=list)
    created_at: datetime


# -----------------------------------------
# 3. Conversation Response
# -----------------------------------------

class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    doctor_id: int
    title: str
    created_at: datetime
    updated_at: datetime


# -----------------------------------------
# 4. Conversation History
# -----------------------------------------

class ConversationHistoryResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int


# -----------------------------------------
# 5. Conversation Detail
# -----------------------------------------

class ConversationDetailResponse(ConversationResponse):
    messages: list[ChatMessageResponse] = Field(
        default_factory=list
    )


# -----------------------------------------
# 6. Chat Response
# -----------------------------------------

class ChatResponse(BaseModel):
    conversation: ConversationResponse
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse


# -----------------------------------------
# 7. Patient Summary Request
# -----------------------------------------

class PatientSummaryRequest(BaseModel):
    force_regenerate: bool = Field(
        default=False,
        description="Generate a fresh summary instead of returning the existing one",
    )


# -----------------------------------------
# 8. Patient Summary Response
# -----------------------------------------


class PatientSummaryCitation(BaseModel):
    record_type: str
    record_id: int
    date: str | None = None
    document_id: int | None = None


class PatientSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    doctor_id: int
    summary: str
    citations: list[PatientSummaryCitation] = Field(
        default_factory=list
    )
    generated_at: datetime

