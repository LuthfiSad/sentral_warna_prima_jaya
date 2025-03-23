from sqlalchemy import Column, String, Integer
from src.config.database import Base

class Face(Base):
    __tablename__ = "faces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    face_id = Column(String, nullable=False, unique=True)
    image_url = Column(String, nullable=False)
