from datetime import datetime, timezone
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.events.review_events import ReviewCreated
from ascend.domain.relationships.entity import EntityType
from ascend.domain.reviews.entity import Difficulty, Review, ReviewStatus, ReviewType


class CreateReviewUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(
        self,
        review_id: UUID,
        entity_id: UUID,
        entity_type: EntityType,
        review_type: ReviewType,
        difficulty: Difficulty = Difficulty.MEDIUM,
        notes: str = "",
    ) -> Review:
        with self.uow:
            # 1. Validate entity existence
            if entity_type == EntityType.CAPTURE:
                if not self.uow.captures.get(entity_id):
                    raise ValueError(f"Capture {entity_id} does not exist.")
            elif entity_type == EntityType.CONCEPT:
                if not self.uow.concepts.get(entity_id):
                    raise ValueError(f"Concept {entity_id} does not exist.")
            elif entity_type == EntityType.SOURCE:
                if not self.uow.sources.get(entity_id):
                    raise ValueError(f"Source {entity_id} does not exist.")
            else:
                raise ValueError(f"Unsupported entity type: {entity_type}")

            # 2. One active review per entity per ReviewType
            existing = self.uow.reviews.find_active_by_entity_and_type(entity_id, review_type)
            if existing:
                raise ValueError(
                    f"A review for entity {entity_id} with type {review_type} already exists."
                )

            now = datetime.now(timezone.utc)
            review = Review(
                id=review_id,
                entity_id=entity_id,
                entity_type=entity_type,
                review_type=review_type,
                status=ReviewStatus.NEW,
                difficulty=difficulty,
                score=0,
                notes=notes,
                created_at=now,
                updated_at=now,
                last_reviewed_at=None,
                next_review_at=now,  # Due immediately
            )

            self.uow.reviews.save(review)
            self.uow.emit(
                ReviewCreated(
                    aggregate_id=review.id,
                    entity_id=str(entity_id),
                    entity_type=entity_type,
                )
            )
            self.uow.commit()

        return review
