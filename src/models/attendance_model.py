# src/models/attendance_model.py
from sqlalchemy import Column, Integer, String, DateTime, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base

class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(Date, nullable=False)
    checkin_time = Column(DateTime(timezone=True), nullable=True)
    checkout_time = Column(DateTime(timezone=True), nullable=True)
    checkin_latitude = Column(Float, nullable=True)
    checkin_longitude = Column(Float, nullable=True)
    checkout_latitude = Column(Float, nullable=True)
    checkout_longitude = Column(Float, nullable=True)
    checkin_image_url = Column(String(500), nullable=True)
    checkout_image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    employee = relationship("Employee", back_populates="attendances")

# Add to Employee model (src/models/employee_model.py)
# Add this line in Employee class:
# attendances = relationship("Attendance", back_populates="employee")