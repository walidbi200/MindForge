from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from ascend.domain.relationships.entity import EntityType


class ReviewType(str, Enum):
    READ = "READ"
    RECALL = "RECALL"
    FLASHCARD = "FLASHCARD"
    QUIZ = "QUIZ"


class ReviewStatus(str, Enum):
    NEW = "NEW"
    LEARNING = "LEARNING"
    REVIEWING = "REVIEWING"
    MASTERED = "MASTERED"
    SUSPENDED = "SUSPENDED"


class Difficulty(str, Enum):
    VERY_EASY = "VERY_EASY"
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    VERY_HARD = "VERY_HARD"


@dataclass
class Review:
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
