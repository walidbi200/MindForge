from datetime import datetime
from uuid import UUID

from sqlmodel import Field, Index, SQLModel

from ascend.domain.relationships.entity import EntityType
from ascend.domain.reviews.entity import ReviewStatus


class ReviewModel(SQLModel, table=True):
    __tablename__ = "reviews"
    __table_args__ = (
        Index("ix_reviews_entity_id", "entity_id"),
        Index("ix_reviews_due_at", "due_at"),
        Index("ix_reviews_status", "status"),
    )

    id: UUID = Field(primary_key=True)
    entity_id: UUID = Field(nullable=False)
    entity_type: EntityType = Field(nullable=False)
    due_at: datetime = Field(nullable=False)
    completed_at: datetime | None = Field(default=None, nullable=True)
    status: ReviewStatus = Field(default=ReviewStatus.PENDING, nullable=False)
    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)
    metadata_json: str = Field(default="{}", nullable=False)
