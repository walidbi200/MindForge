from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from ascend.domain.relationships.entity import EntityType
from ascend.domain.reviews.entity import Difficulty, ReviewStatus, ReviewType


class CreateReviewRequest(BaseModel):
    entity_id: UUID
    entity_type: EntityType
    review_type: ReviewType
    difficulty: Difficulty = Difficulty.MEDIUM
    notes: str = ""


class UpdateReviewRequest(BaseModel):
    status: ReviewStatus | None = None
    difficulty: Difficulty | None = None
    score: int | None = Field(None, ge=0, le=5)
    notes: str | None = None
    next_review_at: datetime | None = None


class CompleteReviewRequest(BaseModel):
    difficulty: Difficulty
    score: int = Field(..., ge=0, le=5)
    notes: str | None = None


class ReviewResponse(BaseModel):
    id: UUID
    entity_id: UUID
    entity_type: EntityType
    review_type: ReviewType
    status: ReviewStatus
    difficulty: Difficulty
    score: int
    notes: str
    created_at: datetime
    updated_at: datetime
    last_reviewed_at: datetime | None = None
    next_review_at: datetime | None = None
