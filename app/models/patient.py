
from __future__ import annotations

from datetime import date

from sqlalchemy import String, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Patient(Base, TimestampMixin):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    patient_uid: Mapped[str] = mapped_column(
        String(30), unique=True, index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)

    dob: Mapped[date | None] = mapped_column(Date, nullable=True)

    gender: Mapped[str | None] = mapped_column(String(30))

    phone: Mapped[str | None] = mapped_column(String(20))

    email: Mapped[str | None] = mapped_column(String(255))

    address: Mapped[str | None] = mapped_column(Text)

    blood_group: Mapped[str | None] = mapped_column(String(10))

    emergency_contact: Mapped[str | None] = mapped_column(String(100))

    medical_history: Mapped[list[MedicalHistory]] = relationship(
        back_populates="patient"
    )

    allergies: Mapped[list[Allergy]] = relationship(
        back_populates="patient"
    )

    appointments: Mapped[list[Appointment]] = relationship(
        back_populates="patient"
    )

    visits: Mapped[list[Visit]] = relationship(
        back_populates="patient"
    )

    documents: Mapped[list[Document]] = relationship(
        back_populates="patient"
    )

    lab_results: Mapped[list[LabResult]] = relationship(
        back_populates="patient"
    )

    document_chunks: Mapped[list[DocumentChunk]] = relationship(
        back_populates="patient"
    )

    audit_logs: Mapped[list[AuditLog]] = relationship(
        back_populates="patient"
    )
