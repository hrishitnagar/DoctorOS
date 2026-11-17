
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentUploadResponse(BaseModel):
    id: int
    patient_id: int
    document_type: str
    ocr_status: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
