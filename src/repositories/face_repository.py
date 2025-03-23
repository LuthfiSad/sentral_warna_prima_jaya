from sqlalchemy.orm import Session
from src.models.face_model import Face

class FaceRepository:
    @staticmethod
    def get_all_faces(db: Session):
        return db.query(Face).all()

    @staticmethod
    def create_face(db: Session, name: str, face_id: str, image_url: str):
        new_face = Face(name=name, face_id=face_id, image_url=image_url)
        db.add(new_face)
        db.commit()
        db.refresh(new_face)
        return new_face
