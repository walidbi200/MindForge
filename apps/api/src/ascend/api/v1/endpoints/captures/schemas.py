from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateCaptureRequest(BaseModel):
    content: str


class CaptureResponse(BaseModel):
    id: UUID
    content: str
    status: str
    created_at: datetime
