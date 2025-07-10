# src/schemas/export_schema.py
from pydantic import BaseModel
from enum import Enum

class StatusUpdateSchema(BaseModel):
    status: str

class ExportFormatEnum(str, Enum):
    EXCEL = "excel"
    PDF = "pdf"