from pydantic import BaseModel, Field

class UserRegisterSchema(BaseModel):
    username: str
    email: str
    password: str = Field(..., min_length=8)

class UserLoginSchema(BaseModel):
    email: str
    password: str

class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True
