from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.events.review_events import ReviewDeleted


class DeleteReviewUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, review_id: UUID) -> bool:
        with self.uow:
            review = self.uow.reviews.get(review_id)
            if not review:
                return False

            self.uow.reviews.delete(review_id)
            self.uow.emit(ReviewDeleted(aggregate_id=review_id))
            self.uow.commit()

        return True
