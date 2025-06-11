from pydantic import BaseModel

class StatusUpdateSchema(BaseModel):
    status: str
