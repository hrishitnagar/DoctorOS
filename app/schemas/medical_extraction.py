
from pydantic import BaseModel, Field


class DiagnosisExtraction(BaseModel):
    name: str
    confidence: float = Field(ge=0, le=1)
    needs_review: bool = True


class MedicineExtraction(BaseModel):
    name: str
    dose: str | None = None
    frequency: str | None = None
    confidence: float = Field(ge=0, le=1)
    needs_review: bool = True


class LabTestExtraction(BaseModel):
    name: str
    value: float
    unit: str | None = None
    reference_range: str | None = None
    confidence: float = Field(ge=0, le=1)
    needs_review: bool = True


class DateExtraction(BaseModel):
    value: str
    type: str


class MedicalExtractionResult(BaseModel):
    diagnoses: list[DiagnosisExtraction] = Field(default_factory=list)
    medicines: list[MedicineExtraction] = Field(default_factory=list)
    lab_tests: list[LabTestExtraction] = Field(default_factory=list)
    dates: list[DateExtraction] = Field(default_factory=list)
