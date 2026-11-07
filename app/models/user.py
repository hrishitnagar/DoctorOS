
from __future__ import annotations

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(150), nullable=False)

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(30), nullable=False, default="doctor"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    appointments: Mapped[list[Appointment]] = relationship(
        back_populates="doctor"
    )

    visits: Mapped[list[Visit]] = relationship(
        back_populates="doctor"
    )

    uploaded_documents: Mapped[list[Document]] = relationship(
        back_populates="uploader"
    )

    audit_logs: Mapped[list[AuditLog]] = relationship(
        back_populates="user"
    )
