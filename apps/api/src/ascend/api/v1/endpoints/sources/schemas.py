from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from ascend.domain.sources.entity import SourceType


class CreateSourceRequest(BaseModel):
    title: str = Field(..., min_length=1)
    source_type: SourceType
    uri: str | None = None
    author: str | None = None
    publisher: str | None = None
    language: str | None = None
    metadata_json: str = "{}"


class UpdateSourceRequest(BaseModel):
    title: str | None = Field(None, min_length=1)
    source_type: SourceType | None = None
    uri: str | None = None
    author: str | None = None
    publisher: str | None = None
    language: str | None = None
    metadata_json: str | None = None


class SourceResponse(BaseModel):
    id: UUID
    title: str
    source_type: SourceType
    uri: str | None
    author: str | None
    publisher: str | None
    language: str | None
    created_at: datetime
    updated_at: datetime
    metadata_json: str
