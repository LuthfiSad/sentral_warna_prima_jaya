# src/models/report_model.py
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Date, Text, Enum, Float
from sqlalchemy.sql import func
from src.config.database import Base
import enum
from sqlalchemy.orm import relationship

class ReportStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    image_url = Column(String(500), nullable=True)
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False)
    report = Column(Text, nullable=False)
    
    # Kolom tambahan
    customer_name = Column(String(255), nullable=False)
    vehicle_type = Column(String(100), nullable=False)
    total_repairs = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    employee = relationship("Employee", back_populates="reports")