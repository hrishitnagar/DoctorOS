from app.models.patient import Patient
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Allergy(Base, TimestampMixin):
    __tablename__ = "allergies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    allergen: Mapped[str] = mapped_column(
        String(200), nullable=False
    )

    reaction: Mapped[str | None] = mapped_column(Text)

    severity: Mapped[str | None] = mapped_column(
        String(30)
    )

    patient: Mapped[Patient] = relationship(
        back_populates="allergies"
    )
