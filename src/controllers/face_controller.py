from fastapi import Depends, UploadFile, File
from sqlalchemy.orm import Session
from src.schemas.face_schema import FaceRegisterSchema
from src.services.face_service import register_face, verify_face
from src.utils.response import handle_response
from src.utils.message_code import MESSAGE_CODE
from src.config.database import get_db

async def register(
    face_data: FaceRegisterSchema,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    image_data = await file.read()
    result = register_face(db, face_data.name, image_data)
    return handle_response(201, MESSAGE_CODE.CREATED, "Face registered successfully", result)

async def verify(file: UploadFile = File(...), db: Session = Depends(get_db)):
    image_data = await file.read()
    result = verify_face(db, image_data)
    return handle_response(200, MESSAGE_CODE.SUCCESS, "Face verification completed", result)
