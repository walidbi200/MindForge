from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.reviews.entity import Review


class ListEntityReviewsUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, entity_id: UUID) -> list[Review]:
        with self.uow:
            return self.uow.reviews.list_by_entity(entity_id)
