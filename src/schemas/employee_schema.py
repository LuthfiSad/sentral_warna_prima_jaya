from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional

class EmployeeCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    date_of_birth: date
    divisi: str = Field(..., min_length=2, max_length=100)
    address: str = Field(..., min_length=5)

class EmployeeUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None
    divisi: Optional[str] = Field(None, min_length=2, max_length=100)
    address: Optional[str] = Field(None, min_length=5)

class EmployeeResponseSchema(BaseModel):
    id: int
    name: str
    email: str
    date_of_birth: date
    divisi: str
    address: str
    image_url: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True