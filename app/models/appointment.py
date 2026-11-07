
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    String, DateTime, ForeignKey, Text, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Appointment(Base, TimestampMixin):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

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

    appointment_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    duration_minutes: Mapped[int] = mapped_column(
    nullable=False,
    default=30,
    server_default="30",
)

    status: Mapped[str] = mapped_column(
        String(30), default="scheduled", nullable=False
    )

    reason: Mapped[str | None] = mapped_column(Text)

    patient: Mapped[Patient] = relationship(
        back_populates="appointments"
    )

    doctor: Mapped[User] = relationship(
        back_populates="appointments"
    )

    visit: Mapped[Visit | None] = relationship(
        back_populates="appointment", uselist=False
    )

    __table_args__ = (
        Index("ix_appointment_doctor_datetime", "doctor_id", "appointment_datetime"),
    )
