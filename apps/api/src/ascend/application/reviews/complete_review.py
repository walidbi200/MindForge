from datetime import datetime, timedelta, timezone
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.events.review_events import ReviewCompleted
from ascend.domain.reviews.entity import Difficulty, Review, ReviewStatus


class CompleteReviewUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(
        self,
        review_id: UUID,
        difficulty: Difficulty,
        score: int,
        notes: str | None = None,
    ) -> Review | None:
        if not (0 <= score <= 5):
            raise ValueError("Score must be between 0 and 5.")

        with self.uow:
            review = self.uow.reviews.get(review_id)
            if not review:
                return None

            now = datetime.now(timezone.utc)
            review.last_reviewed_at = now
            review.difficulty = difficulty
            review.score = score
            if notes is not None:
                review.notes = notes

            # Transitions status based on score
            if score >= 4:
                review.status = ReviewStatus.REVIEWING
            else:
                review.status = ReviewStatus.LEARNING

            # Simple placeholder next review time: 1 day later
            review.next_review_at = now + timedelta(days=1)
            review.updated_at = now

            self.uow.reviews.save(review)
            self.uow.emit(
                ReviewCompleted(
                    aggregate_id=review_id,
                    difficulty=difficulty,
                    score=score,
                )
            )
            self.uow.commit()

        return review
