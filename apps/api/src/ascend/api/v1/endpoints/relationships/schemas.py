from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from ascend.domain.relationships.entity import CreatorType, EntityType, RelationshipType


class CreateRelationshipRequest(BaseModel):
    from_id: UUID
    from_type: EntityType
    to_id: UUID
    to_type: EntityType
    relationship_type: RelationshipType
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    created_by: CreatorType = Field(default=CreatorType.SYSTEM)
    metadata_dict: dict | None = Field(default_factory=dict)


class RelationshipResponse(BaseModel):
    id: UUID
    from_id: UUID
    from_type: EntityType
    to_id: UUID
    to_type: EntityType
    relationship_type: RelationshipType
    confidence: float
    created_by: CreatorType
    created_at: datetime
    metadata_json: str
