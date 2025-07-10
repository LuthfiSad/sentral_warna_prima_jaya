from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from src.config.database import Base
from sqlalchemy.orm import relationship

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)

    # Data mobil
    plate_number = Column(String(20), unique=True, nullable=False)
    vehicle_type = Column(String(100), nullable=False)
    vehicle_model = Column(String(100), nullable=True)
    vehicle_year = Column(String(10), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    transactions = relationship("Transaction", back_populates="customer")
