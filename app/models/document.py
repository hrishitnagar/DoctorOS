
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    String, Text, DateTime, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    document_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    file_path: Mapped[str] = mapped_column(
        String(500), nullable=False
    )

    ocr_status: Mapped[str] = mapped_column(
        String(30), default="pending", nullable=False
    )

    raw_text: Mapped[str | None] = mapped_column(Text)

    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    patient: Mapped[Patient] = relationship(
        back_populates="documents"
    )

    uploader: Mapped[User] = relationship(
        back_populates="uploaded_documents"
    )

    extracted_entities: Mapped[list[ExtractedEntity]] = relationship(
        back_populates="document"
    )

    lab_results: Mapped[list[LabResult]] = relationship(
        back_populates="document"
    )

    chunks: Mapped[list[DocumentChunk]] = relationship(
        back_populates="document"
    )
