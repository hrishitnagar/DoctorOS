from app.models.document import Document
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class ExtractedEntity(Base, TimestampMixin):
    __tablename__ = "extracted_entities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    entity_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    value: Mapped[str] = mapped_column(
        String(500), nullable=False
    )

    unit: Mapped[str | None] = mapped_column(String(50))

    confidence: Mapped[float | None] = mapped_column(Float)

    document: Mapped[Document] = relationship(
        back_populates="extracted_entities"
    )
