from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class MedicineBase(BaseModel):
    name: str
    type: Optional[str] = "tablet"
    dosage_pattern: Optional[str] = None
    instructions: Optional[str] = None
    total_quantity: Optional[int] = None
    duration_days: Optional[int] = None
    purpose: Optional[str] = None

class MedicineCreate(MedicineBase):
    prescription_id: UUID

class MedicineResponse(MedicineBase):
    id: UUID
    prescription_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
