from datetime import datetime
from uuid import UUID

from sqlmodel import Field, Index, SQLModel

from ascend.domain.relationships.entity import CreatorType, EntityType, RelationshipType


class RelationshipModel(SQLModel, table=True):
    __tablename__ = "relationships"
    __table_args__ = (
        Index("ix_relationships_from_id_type", "from_id", "relationship_type"),
        Index("ix_relationships_to_id_type", "to_id", "relationship_type"),
    )

    id: UUID = Field(primary_key=True)
    from_id: UUID = Field(index=True)
    from_type: EntityType = Field(index=True)
    to_id: UUID = Field(index=True)
    to_type: EntityType = Field(index=True)
    relationship_type: RelationshipType = Field(index=True)
    confidence: float
    created_by: CreatorType
    created_at: datetime
    metadata_json: str
