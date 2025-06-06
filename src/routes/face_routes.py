from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from src.middlewares.jwt_auth_username_middleware import check_luthfi_user
from src.schemas.face_schema import FaceRegisterSchema
from src.middlewares.catch_wrapper import catch_exceptions
from src.config.database import get_db
from src.controllers.face_controller import register, verify

router = APIRouter()

@router.post("/register")
@catch_exceptions
async def register_route(
    name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    # user: dict = Depends(check_luthfi_user)  # Add this dependency
):
    return await register(name, file, db)

@router.post("/verify")
@catch_exceptions
async def verify_route(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await verify(file, db)
