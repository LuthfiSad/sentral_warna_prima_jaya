from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.controllers.user_controller import UserController
from src.middlewares.admin_middleware import get_current_user, require_admin
from src.middlewares.catch_wrapper import catch_exceptions
from src.config.database import get_db
from src.middlewares.jwt_auth_middleware import get_current_user_or_none
from src.schemas.user_schema import UserRegisterSchema, UserLoginSchema, UserResetPasswordSchema, UserUpdateSchema

router = APIRouter()

@router.post("/auth/register")
@catch_exceptions
def register_route(user_data: UserRegisterSchema, current_user: Optional[dict] = Depends(get_current_user_or_none), db: Session = Depends(get_db)):
    is_admin = current_user["is_admin"] if current_user else False
    return UserController.register(user_data, is_admin, db)

@router.post("/auth/login")
@catch_exceptions
def login_route(user_data: UserLoginSchema, db: Session = Depends(get_db)):
    return UserController.login(user_data, db)

@router.get("/")
@catch_exceptions
async def get_all_users(
    page: int = Query(1, ge=1),
    perPage: int = Query(10, ge=1, le=100),
    search: str = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await UserController.get_all_users(page, perPage, search, db)

@router.get("/check")
@catch_exceptions
async def check_user(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await UserController.get_user(current_user["user_id"], db)

@router.get("/{user_id}")
@catch_exceptions
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await UserController.get_user(user_id, db)

@router.put("/{user_id}")
@catch_exceptions
async def update_user(
    user_id: int,
    user_data: UserUpdateSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await UserController.update_user(user_id, user_data, db)

@router.post("/reset-password/{user_id}")
@catch_exceptions
async def reset_password(
    user_id: int,
    password_data: UserResetPasswordSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await UserController.reset_password(user_id, password_data, db)

@router.delete("/{user_id}")
@catch_exceptions
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await UserController.delete_user(user_id, db)