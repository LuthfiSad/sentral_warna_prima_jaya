from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.middlewares.catch_wrapper import catch_exceptions
from src.config.database import get_db
from src.controllers.auth_controller import register, login
from src.schemas.user_schema import UserRegisterSchema, UserLoginSchema

router = APIRouter()

@router.post("/register")
@catch_exceptions
def register_route(user_data: UserRegisterSchema, db: Session = Depends(get_db)):
    return register(user_data, db)

@router.post("/login")
@catch_exceptions
def login_route(user_data: UserLoginSchema, db: Session = Depends(get_db)):
    return login(user_data, db)
