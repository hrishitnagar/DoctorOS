
from datetime import datetime, timezone
from typing import Literal
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class AppointmentCreate(BaseModel):
    patient_id: int = Field(gt=0)

    appointment_datetime: datetime

    duration_minutes: int = Field(
        default=30,
        description="Appointment duration: 15, 30, or 60 minutes",
    )

    reason: str | None = Field(default=None, max_length=1000)

    @field_validator("appointment_datetime")
    @classmethod
    def validate_appointment_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                "Appointment datetime must include a timezone"
            )

        if value <= datetime.now(timezone.utc):
            raise ValueError(
                "Appointment must be scheduled in the future"
            )

        return value

    @field_validator("duration_minutes")
    @classmethod
    def validate_duration(cls, value: int) -> int:
        if value not in {15, 30, 60}:
            raise ValueError(
                "Duration must be 15, 30, or 60 minutes"
            )

        return value



class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    doctor_id: int
    appointment_datetime: datetime
    duration_minutes: int
    status: str
    reason: str | None = None


class AppointmentStatusUpdate(BaseModel):
    status: Literal["completed", "cancelled", "no-show"]



