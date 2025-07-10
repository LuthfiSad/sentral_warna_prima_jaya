# src/schemas/report_schema.py
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class ReportStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"

class ReportCreateSchema(BaseModel):
    transaction_id: int
    description: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @validator('description')
    def validate_description(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Description is required')
        return v.strip()

class ReportUpdateSchema(BaseModel):
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class ReportStatusUpdateSchema(BaseModel):
    status: ReportStatusEnum
    rejection_reason: Optional[str] = None

    @validator('rejection_reason')
    def validate_rejection_reason(cls, v, values):
        if values.get('status') == ReportStatusEnum.REJECTED and not v:
            raise ValueError('Rejection reason is required when rejecting report')
        return v

class ReportResponseSchema(BaseModel):
    id: int
    transaction_id: int
    employee_id: int
    description: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    image_url: Optional[str]
    status: str
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    employee: Optional[dict] = None
    transaction: Optional[dict] = None

    class Config:
        from_attributes = True