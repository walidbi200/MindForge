from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateConceptRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    summary: str = Field(..., max_length=10000)


class UpdateConceptRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    summary: str | None = Field(default=None, max_length=10000)


class ConceptResponse(BaseModel):
    id: UUID
    title: str
    summary: str
    created_at: datetime
    updated_at: datetime
