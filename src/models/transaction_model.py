from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, Enum, Float
from sqlalchemy.sql import func
from src.config.database import Base
from sqlalchemy.orm import relationship
import enum

class TransactionStatus(enum.Enum):
    PENDING = "PENDING"
    PROSES = "PROSES"
    MENUNGGU_APPROVAL = "MENUNGGU_APPROVAL"
    SELESAI = "SELESAI"
    DIBAYAR = "DIBAYAR"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    complaint = Column(Text, nullable=True)
    total_cost = Column(Float, nullable=True)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    customer = relationship("Customer", back_populates="transactions")
    reports = relationship("Report", back_populates="transaction")
    histories = relationship("History", back_populates="transaction")
