
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    String, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    patient_id: Mapped[int | None] = mapped_column(
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )

    action: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    resource_type: Mapped[str | None] = mapped_column(
        String(100)
    )

    resource_id: Mapped[str | None] = mapped_column(
        String(100)
    )

    details: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    user: Mapped[User | None] = relationship(
        back_populates="audit_logs"
    )

    patient: Mapped[Patient | None] = relationship(
        back_populates="audit_logs"
    )
