
from __future__ import annotations

from datetime import date

from sqlalchemy import (
    String, Float, Date, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class LabResult(Base, TimestampMixin):
    __tablename__ = "lab_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )

    test_name: Mapped[str] = mapped_column(
        String(200), nullable=False
    )

    value: Mapped[float] = mapped_column(nullable=False)

    unit: Mapped[str | None] = mapped_column(String(50))

    ref_range: Mapped[str | None] = mapped_column(String(100))

    test_date: Mapped[date] = mapped_column(
        Date, nullable=False, index=True
    )

    patient: Mapped[Patient] = relationship(
        back_populates="lab_results"
    )

    document: Mapped[Document | None] = relationship(
        back_populates="lab_results"
    )
