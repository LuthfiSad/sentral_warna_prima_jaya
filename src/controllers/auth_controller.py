from fastapi import Depends
from sqlalchemy.orm import Session
from src.schemas.user_schema import UserRegisterSchema, UserLoginSchema
from src.services.auth_service import register_user, authenticate_user
from src.utils.response import handle_response
from src.utils.message_code import MESSAGE_CODE
from src.config.database import get_db

def register(user_data: UserRegisterSchema, db: Session = Depends(get_db)):
    register_user(db, user_data.username, user_data.email, user_data.password)
    return handle_response(201, MESSAGE_CODE.CREATED, "User registered successfully")

def login(user_data: UserLoginSchema, db: Session = Depends(get_db)):
    token = authenticate_user(db, user_data.email, user_data.password)
    return handle_response(200, MESSAGE_CODE.SUCCESS, "Login successful", token)
