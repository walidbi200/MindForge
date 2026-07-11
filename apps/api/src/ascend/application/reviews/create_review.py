from datetime import datetime, timezone
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.events.review_events import ReviewCreated
from ascend.domain.exceptions import ConflictError, EntityNotFoundError, InvalidEntityStateError
from ascend.domain.relationships.entity import EntityType
from ascend.domain.reviews.entity import Review, ReviewStatus


class CreateReviewUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(
        self,
        review_id: UUID,
        entity_id: UUID,
        entity_type: EntityType,
        due_at: datetime,
        metadata_json: str = "{}",
    ) -> Review:
        with self.uow:
            # 1. Validate entity exists
            if entity_type == EntityType.CAPTURE:
                if not self.uow.captures.get(entity_id):
                    raise EntityNotFoundError(f"Capture {entity_id} does not exist.")
            elif entity_type == EntityType.CONCEPT:
                if not self.uow.concepts.get(entity_id):
                    raise EntityNotFoundError(f"Concept {entity_id} does not exist.")
            elif entity_type == EntityType.SOURCE:
                if not self.uow.sources.get(entity_id):
                    raise EntityNotFoundError(f"Source {entity_id} does not exist.")
            else:
                raise InvalidEntityStateError(f"Unsupported entity type: {entity_type}")

            # 2. Block if entity already has a PENDING review
            existing_reviews = self.uow.reviews.list_by_entity(entity_id)
            if any(r.status == ReviewStatus.PENDING for r in existing_reviews):
                raise ConflictError("Entity already has a pending review.")

            now = datetime.now(timezone.utc)
            review = Review(
                id=review_id,
                entity_id=entity_id,
                entity_type=entity_type,
                due_at=due_at,
                completed_at=None,
                status=ReviewStatus.PENDING,
                created_at=now,
                updated_at=now,
                metadata_json=metadata_json,
            )

            self.uow.reviews.save(review)
            self.uow.emit(
                ReviewCreated(
                    aggregate_id=review_id,
                    entity_id=str(entity_id),
                    entity_type=entity_type,
                )
            )
            self.uow.commit()

        return review
