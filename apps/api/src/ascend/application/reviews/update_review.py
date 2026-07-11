from datetime import datetime, timezone
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.events.review_events import ReviewUpdated
from ascend.domain.reviews.entity import Difficulty, Review, ReviewStatus


class UpdateReviewUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(
        self,
        review_id: UUID,
        status: ReviewStatus | None = None,
        difficulty: Difficulty | None = None,
        score: int | None = None,
        notes: str | None = None,
        next_review_at: datetime | None = None,
    ) -> Review | None:
        with self.uow:
            review = self.uow.reviews.get(review_id)
            if not review:
                return None

            if status is not None:
                review.status = status
            if difficulty is not None:
                review.difficulty = difficulty
            if score is not None:
                review.score = score
            if notes is not None:
                review.notes = notes
            if next_review_at is not None:
                review.next_review_at = next_review_at

            review.updated_at = datetime.now(timezone.utc)

            self.uow.reviews.save(review)
            self.uow.emit(ReviewUpdated(aggregate_id=review_id))
            self.uow.commit()

        return review
