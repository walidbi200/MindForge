from ascend.application.uow import UnitOfWork
from ascend.domain.reviews.entity import Review


class ListReviewsUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, offset: int = 0, limit: int = 100) -> list[Review]:
        with self.uow:
            return self.uow.reviews.list(offset=offset, limit=limit)
