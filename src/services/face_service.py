import dlib
import numpy as np
from PIL import Image
from io import BytesIO
from sqlalchemy.orm import Session
from src.repositories.face_repository import FaceRepository
from src.libs.supabase import upload_image_to_supabase
from src.utils.error import AppError
from src.utils.message_code import MESSAGE_CODE
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "models-face")

SP_MODEL_PATH = os.path.join(MODEL_DIR, "shape_predictor_68_face_landmarks.dat")
FACE_REC_MODEL_PATH = os.path.join(MODEL_DIR, "dlib_face_recognition_resnet_model_v1.dat")

detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(SP_MODEL_PATH)
face_rec_model = dlib.face_recognition_model_v1(FACE_REC_MODEL_PATH)

async def register_face(db: Session, name: str, image_data: bytes):
    image = Image.open(BytesIO(image_data)).convert("RGB")
    img = np.array(image)

    faces = detector(img)
    if len(faces) == 0:
        raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "No face detected")

    shape = sp(img, faces[0])
    face_encoding = np.array(face_rec_model.compute_face_descriptor(img, shape))

    face_id = ','.join(map(str, face_encoding))

    image_url = await upload_image_to_supabase(image_data)
    if type(image_url) is AppError:
        raise image_url

    new_face = FaceRepository.create_face(db, name, face_id, image_url)
    return {"message": "Face registered successfully", "url": new_face.image_url}

def verify_face(db: Session, image_data: bytes):
    image = Image.open(BytesIO(image_data)).convert("RGB")
    img = np.array(image)

    faces = detector(img)
    if len(faces) == 0:
        raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "No face detected")

    shape = sp(img, faces[0])
    face_encoding = np.array(face_rec_model.compute_face_descriptor(img, shape))

    known_faces = FaceRepository.get_all_faces(db)

    for face in known_faces:
        known_encoding = np.array(list(map(float, face.face_id.split(','))))
        distance = np.linalg.norm(face_encoding - known_encoding)
        if distance < 0.6:
            return {"message": "Face recognized", "image_url": face.image_url, "name": face.name}

    raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Face not recognized")
