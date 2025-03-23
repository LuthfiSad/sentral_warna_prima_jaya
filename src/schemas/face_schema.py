from pydantic import BaseModel
from fastapi import UploadFile, File

class FaceRegisterSchema(BaseModel):
     name: str
