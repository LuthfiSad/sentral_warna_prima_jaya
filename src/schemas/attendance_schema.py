from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class AttendanceResponseSchema(BaseModel):
    id: int
    date: date
    checkin_time: Optional[datetime]
    checkout_time: Optional[datetime]
    # Tambahkan field lain sesuai kebutuhan

    class Config:
        from_attributes = True