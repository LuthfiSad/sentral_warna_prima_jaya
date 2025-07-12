from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, Enum, String
from sqlalchemy.sql import func
from src.config.database import Base
from sqlalchemy.orm import relationship
import enum

class ReportStatus(enum.Enum):
    APPROVED = "APPROVED"
    PENDING = "PENDING"
    REJECTED = "REJECTED"

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)  # Using string reference
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    description = Column(Text, nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    image_url = Column(String(500), nullable=True)

    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False)
    approved_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    approved_user_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    transaction = relationship("Transaction", back_populates="reports")  # Using string reference
    employee = relationship("Employee", foreign_keys=[employee_id])
    approver = relationship("Employee", foreign_keys=[approved_by])
    user = relationship("User", foreign_keys=[approved_user_by])