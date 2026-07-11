from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.reviews.entity import Review


class GetReviewUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, review_id: UUID) -> Review | None:
        with self.uow:
            return self.uow.reviews.get(review_id)
