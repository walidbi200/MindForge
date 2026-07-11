from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.collections.entity import Collection


class GetCollectionUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, collection_id: UUID) -> Collection | None:
        with self.uow:
            return self.uow.collections.get(collection_id)
