
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    ForeignKey, Text, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Visit(Base, TimestampMixin):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    appointment_id: Mapped[int | None] = mapped_column(
        ForeignKey("appointments.id", ondelete="RESTRICT"),
        unique=True,
        nullable=True
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    observations: Mapped[str | None] = mapped_column(Text)

    diagnosis: Mapped[str | None] = mapped_column(Text)

    prescription_notes: Mapped[str | None] = mapped_column(Text)

    visit_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    patient: Mapped[Patient] = relationship(
        back_populates="visits"
    )

    doctor: Mapped[User] = relationship(
        back_populates="visits"
    )

    appointment: Mapped[Appointment | None] = relationship(
        back_populates="visit"
    )

    medications: Mapped[list[Medication]] = relationship(
        back_populates="visit"
    )
