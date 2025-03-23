from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from src.schemas.face_schema import FaceRegisterSchema
from src.middlewares.catch_wrapper import catch_exceptions
from src.config.database import get_db
from src.controllers.face_controller import register, verify

router = APIRouter(prefix="/face", tags=["Face Recognition"])

@router.post("/register/")
@catch_exceptions
async def register_route(
    face_data: FaceRegisterSchema,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return await register(face_data, file, db)

@router.post("/verify/")
@catch_exceptions
async def verify_route(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await verify(file, db)
