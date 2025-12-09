from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from .medicine_models import MedicineResponse

class PrescriptionBase(BaseModel):
    doctor_name: Optional[str] = None
    patient_name: Optional[str] = None
    notes: Optional[str] = None

class PrescriptionCreate(PrescriptionBase):
    image_base64: Optional[str] = None # Or handle file upload separately
    medicines: List[dict] # Simplified for creation payload

class PrescriptionResponse(PrescriptionBase):
    id: UUID
    user_id: UUID
    image_url: str
    created_at: datetime
    updated_at: datetime
    medicines: List[MedicineResponse] = []

    class Config:
        from_attributes = True
