from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, Text
from sqlalchemy.sql import func
from src.config.database import Base
import enum
from sqlalchemy.orm import relationship

class TransactionStatus(enum.Enum):
    PENDING = "pending"
    PROSES = "proses"
    MENUNGGU_APPROVAL = "menunggu_approval"
    SELESAI = "selesai"
    DIBAYAR = "dibayar"

class History(Base):
    __tablename__ = "histories"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    status = Column(Enum(TransactionStatus), nullable=False)
    note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transaction = relationship("Transaction", back_populates="histories")
