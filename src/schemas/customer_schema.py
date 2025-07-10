# src/schemas/customer_schema.py
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class CustomerCreateSchema(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    plate_number: str
    vehicle_type: str
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[str] = None

    @validator('plate_number')
    def validate_plate_number(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Plate number is required')
        return v.strip().upper()

class CustomerUpdateSchema(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    vehicle_type: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[str] = None

class CustomerResponseSchema(BaseModel):
    id: int
    name: str
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    plate_number: str
    vehicle_type: str
    vehicle_model: Optional[str]
    vehicle_year: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True