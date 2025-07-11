# src/models/employee_model.py
from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.config.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    divisi = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    face_encoding = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    attendances = relationship("Attendance", back_populates="employee")
    
    # Reports created by this employee
    reports = relationship(
        "Report", 
        foreign_keys="[Report.employee_id]",
        back_populates="employee"
    )
    
    # Reports approved by this employee
    approved_reports = relationship(
        "Report",
        foreign_keys="[Report.approved_by]",
        back_populates="approver"
    )