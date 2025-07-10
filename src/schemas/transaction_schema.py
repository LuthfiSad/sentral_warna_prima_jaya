# src/schemas/transaction_schema.py
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class TransactionStatusEnum(str, Enum):
    PENDING = "pending"
    PROSES = "proses"
    MENUNGGU_APPROVAL = "menunggu_approval"
    SELESAI = "selesai"
    DIBAYAR = "dibayar"

class TransactionCreateSchema(BaseModel):
    customer_id: int
    complaint: str

    @validator('complaint')
    def validate_complaint(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Complaint description is required')
        return v.strip()

class TransactionUpdateSchema(BaseModel):
    complaint: Optional[str] = None
    total_cost: Optional[float] = None

class TransactionStatusUpdateSchema(BaseModel):
    status: TransactionStatusEnum
    note: Optional[str] = None

class TransactionResponseSchema(BaseModel):
    id: int
    customer_id: int
    complaint: str
    total_cost: Optional[float]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    customer: Optional[dict] = None
    reports: Optional[list] = None

    class Config:
        from_attributes = True