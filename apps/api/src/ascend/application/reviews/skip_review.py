from datetime import datetime, timezone
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.events.review_events import ReviewSkipped
from ascend.domain.exceptions import EntityNotFoundError, InvalidEntityStateError
from ascend.domain.reviews.entity import Review, ReviewStatus


class SkipReviewUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, review_id: UUID) -> Review:
        with self.uow:
            review = self.uow.reviews.get(review_id)
            if not review:
                raise EntityNotFoundError(f"Review {review_id} not found")

            if review.status != ReviewStatus.PENDING:
                raise InvalidEntityStateError(f"Cannot skip review in status {review.status}")

            now = datetime.now(timezone.utc)
            review.status = ReviewStatus.SKIPPED
            review.updated_at = now

            self.uow.reviews.save(review)
            self.uow.emit(ReviewSkipped(aggregate_id=review_id))
            self.uow.commit()

        return review
