
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ExtractedEntityUpdate(BaseModel):
    value: str | None = Field(default=None, max_length=500)
    unit: str | None = Field(default=None, max_length=50)


class LabResultUpdate(BaseModel):
    test_name: str | None = Field(default=None, max_length=200)
    value: float | None = None
    unit: str | None = Field(default=None, max_length=50)
    ref_range: str | None = Field(default=None, max_length=100)
    test_date: date | None = None


class ReviewRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    review_status: str
    needs_review: bool
    reviewed_by: int | None
    reviewed_at: datetime | None


class ReviewDecision(BaseModel):
    decision: str = Field(pattern="^(approved|rejected)$")
