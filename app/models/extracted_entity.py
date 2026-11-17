
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    String,
    Float,
    ForeignKey,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin
from app.models.document import Document


class ExtractedEntity(Base, TimestampMixin):
    __tablename__ = "extracted_entities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    entity_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    value: Mapped[str] = mapped_column(
        String(500), nullable=False
    )

    needs_review: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    unit: Mapped[str | None] = mapped_column(String(50))

    confidence: Mapped[float | None] = mapped_column(Float)

    # Human verification fields
    review_status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        server_default="pending",
        nullable=False,
    )

    reviewed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    document: Mapped[Document] = relationship(
        back_populates="extracted_entities"
    )
