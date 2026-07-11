from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel

from ascend.domain.sources.entity import SourceType


class SourceModel(SQLModel, table=True):
    __tablename__ = "sources"

    id: UUID = Field(primary_key=True)
    title: str = Field(index=True)
    source_type: SourceType = Field(index=True)
    uri: str | None = Field(default=None, index=True)
    author: str | None = None
    publisher: str | None = None
    language: str | None = None
    created_at: datetime
    updated_at: datetime
    metadata_json: str = "{}"
