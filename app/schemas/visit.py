
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class MedicationCreate(BaseModel):
    drug: str = Field(min_length=1, max_length=200)
    dose: str | None = Field(default=None, max_length=100)
    frequency: str | None = Field(default=None, max_length=100)
    duration: str | None = Field(default=None, max_length=100)
    instructions: str | None = None


class VisitCreate(BaseModel):
    patient_id: int = Field(gt=0)
    appointment_id: int | None = Field(default=None, gt=0)

    observations: str | None = None
    diagnosis: str | None = None
    prescription_notes: str | None = None

    visit_date: datetime

    medications: list[MedicationCreate] = Field(default_factory=list)


class MedicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    drug: str
    dose: str | None = None
    frequency: str | None = None
    duration: str | None = None
    instructions: str | None = None


class VisitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    appointment_id: int | None = None
    patient_id: int
    doctor_id: int

    observations: str | None = None
    diagnosis: str | None = None
    prescription_notes: str | None = None
    visit_date: datetime

    medications: list[MedicationResponse] = Field(default_factory=list)
