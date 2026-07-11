from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.sources.entity import Source


class GetSourceUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, source_id: UUID) -> Source | None:
        with self.uow:
            return self.uow.sources.get(source_id)
