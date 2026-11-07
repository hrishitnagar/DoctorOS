
from datetime import date
from app.models.patient import Patient
from sqlalchemy import String, Date, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class MedicalHistory(Base, TimestampMixin):
    __tablename__ = "medical_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    condition: Mapped[str] = mapped_column(
        String(200), nullable=False
    )

    since: Mapped[date | None] = mapped_column(Date)

    notes: Mapped[str | None] = mapped_column(Text)

    patient: Mapped[Patient] = relationship(
        back_populates="medical_history"
    )
