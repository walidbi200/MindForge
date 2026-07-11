from datetime import datetime
from uuid import UUID

from sqlmodel import Field, Index, SQLModel

from ascend.domain.relationships.entity import EntityType


class CollectionModel(SQLModel, table=True):
    __tablename__ = "collections"

    id: UUID = Field(primary_key=True)
    name: str = Field(index=True, sa_column_kwargs={"unique": True})
    description: str
    color: str
    icon: str
    created_at: datetime
    updated_at: datetime
    metadata_json: str = "{}"


class MembershipModel(SQLModel, table=True):
    __tablename__ = "memberships"
    __table_args__ = (
        Index(
            "ix_membership_unique",
            "collection_id",
            "entity_id",
            "entity_type",
            unique=True,
        ),
    )

    id: UUID = Field(primary_key=True)
    collection_id: UUID = Field(index=True)
    entity_id: UUID = Field(index=True)
    entity_type: EntityType = Field(index=True)
    created_at: datetime
