from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from ascend.domain.relationships.entity import EntityType
from ascend.domain.reviews.entity import ReviewStatus


class CreateReviewRequest(BaseModel):
    entity_id: UUID
    entity_type: EntityType
    due_at: datetime
    metadata_json: str = "{}"


class CompleteReviewRequest(BaseModel):
    metadata_json: str | None = None


class ReviewResponse(BaseModel):
    id: UUID
    entity_id: UUID
    entity_type: EntityType
    due_at: datetime
    completed_at: datetime | None
    status: ReviewStatus
    created_at: datetime
    updated_at: datetime
    metadata_json: str

    model_config = ConfigDict(from_attributes=True)
