

from datetime import date
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.conversation_message import ConversationMessage
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.patient import Patient
from app.schemas.patient import PatientCreate
class ConversationError(Exception):
    """Raised when conversation processing fails."""


def create_patient(db: Session, patient_data: PatientCreate) -> Patient:
    """
    Create a patient and generate a unique patient UID.

    Format: DOS-YYYY-000001
    """

    current_year = date.today().year

    # Temporary unique UID before the database generates the patient ID.
    temporary_uid = f"T-{uuid4().hex[:20]}"

    patient = Patient(
        **patient_data.model_dump(),
        patient_uid=temporary_uid,
    )

    try:
        db.add(patient)

        # Insert the patient and generate its database ID.
        db.flush()

        # Generate the permanent patient UID using the database ID.
        patient.patient_uid = (
            f"DOS-{current_year}-{patient.id:06d}"
        )

        db.commit()
        db.refresh(patient)

        return patient

    except Exception:
        db.rollback()
        raise


def get_patients(
    db: Session,
    search: str | None = None,
    skip: int = 0,
    limit: int = 10,
):
    query = db.query(Patient)

    if search:
        search_term = f"%{search.strip()}%"

        query = query.filter(
            or_(
                Patient.name.ilike(search_term),
                Patient.phone.ilike(search_term),
                Patient.patient_uid.ilike(search_term),
            )
        )

    total = query.count()

    patients = (
        query
        .order_by(Patient.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return patients, total

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

