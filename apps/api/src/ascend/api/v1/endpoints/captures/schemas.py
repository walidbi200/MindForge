from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class CreateCaptureRequest(BaseModel):
    content: str

class CaptureResponse(BaseModel):
    id: UUID
    content: str
    created_at: datetime
