from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from ascend.domain.relationships.entity import EntityType


class CreateCollectionRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""
    color: str = "#3B82F6"
    icon: str = "book"
    metadata_json: str = "{}"


class UpdateCollectionRequest(BaseModel):
    name: str | None = Field(None, min_length=1)
    description: str | None = None
    color: str | None = None
    icon: str | None = None
    metadata_json: str | None = None


class CollectionResponse(BaseModel):
    id: UUID
    name: str
    description: str
    color: str
    icon: str
    created_at: datetime
    updated_at: datetime
    metadata_json: str


class AddEntityRequest(BaseModel):
    entity_id: UUID
    entity_type: EntityType


class MembershipResponse(BaseModel):
    id: UUID
    collection_id: UUID
    entity_id: UUID
    entity_type: EntityType
    created_at: datetime
