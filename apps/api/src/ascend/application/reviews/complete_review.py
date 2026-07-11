from datetime import datetime, timezone
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.events.review_events import ReviewCompleted
from ascend.domain.exceptions import EntityNotFoundError, InvalidEntityStateError
from ascend.domain.reviews.entity import Review, ReviewStatus


class CompleteReviewUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, review_id: UUID, new_metadata_json: str | None = None) -> Review:
        with self.uow:
            review = self.uow.reviews.get(review_id)
            if not review:
                raise EntityNotFoundError(f"Review {review_id} not found")

            if review.status != ReviewStatus.PENDING:
                raise InvalidEntityStateError(f"Cannot complete review in status {review.status}")

            now = datetime.now(timezone.utc)
            review.status = ReviewStatus.COMPLETED
            review.completed_at = now
            review.updated_at = now
            if new_metadata_json is not None:
                review.metadata_json = new_metadata_json

            self.uow.reviews.save(review)
            self.uow.emit(ReviewCompleted(aggregate_id=review_id))
            self.uow.commit()

        return review
