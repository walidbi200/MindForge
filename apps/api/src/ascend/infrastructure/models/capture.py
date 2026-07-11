from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel


class CaptureModel(SQLModel, table=True):
    __tablename__ = "captures"

    id: UUID = Field(primary_key=True)
    content: str
    status: str = Field(default="PENDING", index=True)
    created_at: datetime
