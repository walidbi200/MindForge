from ascend.application.uow import UnitOfWork
from ascend.domain.sources.entity import Source, SourceType


class ListSourcesUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, limit: int = 50, offset: int = 0, source_type: SourceType | None = None) -> list[Source]:
        with self.uow:
            return self.uow.sources.list(limit=limit, offset=offset, source_type=source_type)
