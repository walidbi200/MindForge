from datetime import datetime, timezone

from ascend.application.uow import UnitOfWork
from ascend.domain.reviews.entity import Review


class ListDueReviewsUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self) -> list[Review]:
        now = datetime.now(timezone.utc)
        with self.uow:
            return self.uow.reviews.list_due(now)
