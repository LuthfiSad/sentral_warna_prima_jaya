# src/schemas/history_schema.py
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class TransactionStatusEnum(str, Enum):
    PENDING = "PENDING"
    PROSES = "PROSES"
    SELESAI = "SELESAI"
    DIBAYAR = "DIBAYAR"

class HistoryCreateSchema(BaseModel):
    transaction_id: int
    status: TransactionStatusEnum
    note: Optional[str] = None

    @validator('note')
    def validate_note(cls, v):
        if v and len(v.strip()) == 0:
            return None
        return v.strip() if v else None

class HistoryResponseSchema(BaseModel):
    id: int
    transaction_id: int
    status: str
    note: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    employee: Optional[dict] = None
    transaction: Optional[dict] = None

    class Config:
        from_attributes = True
