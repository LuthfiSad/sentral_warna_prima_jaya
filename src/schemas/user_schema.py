from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from src.schemas.employee_schema import EmployeeUserResponseSchema

class UserRegisterSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    is_admin: Optional[bool] = False
    key_admin: Optional[str] = None
    password: str = Field(..., min_length=8)

class UserLoginSchema(BaseModel):
    login: str  # bisa email atau username
    password: str
    
class UserUpdateSchema(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    is_admin: Optional[bool] = None

class UserResetPasswordSchema(BaseModel):
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    def validate_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    karyawan_id: Optional[int]
    employee: Optional[EmployeeUserResponseSchema] = None

    class Config:
        from_attributes = True