
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.conversation_message import ConversationMessage
from app.models.patient import Patient
from app.models.user import User

from app.services.rag_pipeline_service import (
    run_rag_pipeline,
    RAGPipelineError,
)


class ConversationError(Exception):
    """Raised when conversation processing fails."""


def get_or_create_conversation(
    db: Session,
    patient_id: int,
    doctor_id: int,
    conversation_id: int | None = None,
) -> Conversation:
    """
    Retrieve an existing authorized conversation
    or create a new one.
    """

    if conversation_id is not None:
        conversation = (
            db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.patient_id == patient_id,
                Conversation.doctor_id == doctor_id,
            )
            .first()
        )

        if not conversation:
            raise ConversationError(
                "Conversation not found or access denied."
            )

        return conversation

    conversation = Conversation(
        patient_id=patient_id,
        doctor_id=doctor_id,
        title="New Conversation",
    )

    db.add(conversation)
    db.flush()

    return conversation


def run_patient_chat(
    db: Session,
    patient_id: int,
    doctor_id: int,
    question: str,
    conversation_id: int | None = None,
) -> dict:
    """
    Process a patient chat request.

    Conversation history is used only to interpret
    follow-up questions. Medical facts must come
    from the patient-specific RAG retrieval.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    try:
        conversation = get_or_create_conversation(
            db=db,
            patient_id=patient_id,
            doctor_id=doctor_id,
            conversation_id=conversation_id,
        )

        # Retrieve recent messages for follow-up context.
        previous_messages = (
            db.query(ConversationMessage)
            .filter(
                ConversationMessage.conversation_id == conversation.id
            )
            .order_by(ConversationMessage.created_at.desc())
            .limit(10)
            .all()
        )

        previous_messages.reverse()

        history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in previous_messages
            if message.role in ("user", "assistant")
        ]

        # Save the doctor's question.
        user_message = ConversationMessage(
            conversation_id=conversation.id,
            role="user",
            content=question.strip(),
            citations=[],
        )

        db.add(user_message)
        db.flush()

        # Run the existing RAG pipeline.
        # At this stage history is collected but not yet
        # passed to Gemini. We will add safe follow-up
        # question handling in the next implementation step.
        result = run_rag_pipeline(
            db=db,
            patient_id=patient_id,
            question=question.strip(),
        )

        # Update title using the first question.
        if conversation.title == "New Conversation":
            conversation.title = question.strip()[:60]

        # Save the AI response.
        assistant_message = ConversationMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=result["answer"],
            citations=result["citations"],
        )

        db.add(assistant_message)
        db.flush()

        db.commit()

        db.refresh(conversation)
        db.refresh(user_message)
        db.refresh(assistant_message)

        return {
            "conversation": conversation,
            "user_message": user_message,
            "assistant_message": assistant_message,
        }

    except Exception:
        db.rollback()
        raise

def get_patient_conversations(
    db: Session,
    patient_id: int,
    doctor_id: int,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Conversation], int]:
    """
    Return conversations belonging to a specific doctor and patient.
    Supports pagination.
    """

    query = db.query(Conversation).filter(
        Conversation.patient_id == patient_id,
        Conversation.doctor_id == doctor_id,
    )

    total = query.count()

    conversations = (
        query
        .order_by(Conversation.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return conversations, total


def get_conversation_detail(
    db: Session,
    patient_id: int,
    doctor_id: int,
    conversation_id: int,
) -> Conversation:
    """
    Return one conversation with its messages.
    Only the owning doctor can access it.
    """

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.patient_id == patient_id,
            Conversation.doctor_id == doctor_id,
        )
        .first()
    )

    if not conversation:
        raise ConversationError(
            "Conversation not found or access denied."
        )

    return conversation

