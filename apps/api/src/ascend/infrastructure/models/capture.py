from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field

class CaptureModel(SQLModel, table=True):
    __tablename__ = "captures"
    
    id: UUID = Field(primary_key=True)
    content: str
    created_at: datetime
