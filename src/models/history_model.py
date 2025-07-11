from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, Text
from sqlalchemy.sql import func
from src.config.database import Base
import enum
from sqlalchemy.orm import relationship

class TransactionStatus(enum.Enum):
    PENDING = "PENDING"
    PROSES = "PROSES"
    MENUNGGU_APPROVAL = "MENUNGGU_APPROVAL"
    SELESAI = "SELESAI"
    DIBAYAR = "DIBAYAR"

class History(Base):
    __tablename__ = "histories"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(TransactionStatus), nullable=False)
    note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transaction = relationship("Transaction", back_populates="histories")
    user = relationship("User", foreign_keys=[created_by])
