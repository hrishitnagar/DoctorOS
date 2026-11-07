from app.models.visit import Visit
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Medication(Base, TimestampMixin):
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    visit_id: Mapped[int] = mapped_column(
        ForeignKey("visits.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    drug: Mapped[str] = mapped_column(
        String(200), nullable=False
    )

    dose: Mapped[str | None] = mapped_column(String(100))

    frequency: Mapped[str | None] = mapped_column(String(100))

    duration: Mapped[str | None] = mapped_column(String(100))

    instructions: Mapped[str | None] = mapped_column(Text)

    visit: Mapped[Visit] = relationship(
        back_populates="medications"
    )
