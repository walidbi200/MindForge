from datetime import datetime
from uuid import UUID

from sqlmodel import Field, Index, SQLModel

from ascend.domain.relationships.entity import EntityType
from ascend.domain.reviews.entity import Difficulty, ReviewStatus, ReviewType


class ReviewModel(SQLModel, table=True):
    __tablename__ = "reviews"
    __table_args__ = (
        Index("ix_reviews_entity_id", "entity_id"),
        Index("ix_reviews_entity_type", "entity_type"),
        Index("ix_reviews_status", "status"),
        Index("ix_reviews_next_review_at", "next_review_at"),
    )

    id: UUID = Field(primary_key=True)
    entity_id: UUID = Field(nullable=False)
    entity_type: EntityType = Field(nullable=False)
    review_type: ReviewType = Field(nullable=False)
    status: ReviewStatus = Field(default=ReviewStatus.NEW, nullable=False)
    difficulty: Difficulty = Field(default=Difficulty.MEDIUM, nullable=False)
    score: int = Field(default=0, nullable=False)
    notes: str = Field(default="", nullable=False)
    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)
    last_reviewed_at: datetime | None = Field(default=None, nullable=True)
    next_review_at: datetime | None = Field(default=None, nullable=True)
