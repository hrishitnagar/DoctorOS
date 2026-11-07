
from __future__ import annotations

from sqlalchemy import Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.database.base import Base, TimestampMixin


class DocumentChunk(Base, TimestampMixin):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    chunk_text: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(), nullable=True
    )

    page_no: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    document: Mapped[Document] = relationship(
        back_populates="chunks"
    )

    patient: Mapped[Patient] = relationship(
        back_populates="document_chunks"
    )
