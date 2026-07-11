from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from ascend.domain.relationships.entity import EntityType


class ReviewStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"


@dataclass
class Review:
    id: UUID
    entity_id: UUID
    entity_type: EntityType
    due_at: datetime
    completed_at: datetime | None
    status: ReviewStatus
    created_at: datetime
    updated_at: datetime
    metadata_json: str = "{}"
