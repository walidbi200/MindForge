from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel


class ConceptModel(SQLModel, table=True):
    __tablename__ = "concepts"

    id: UUID = Field(primary_key=True)
    title: str
    summary: str
    created_at: datetime
    updated_at: datetime
