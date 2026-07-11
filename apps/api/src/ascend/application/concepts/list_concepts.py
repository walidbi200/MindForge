from ascend.application.uow import UnitOfWork
from ascend.domain.concepts.entity import Concept


class ListConceptsUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, limit: int = 50, offset: int = 0, q: str | None = None) -> list[Concept]:
        with self.uow:
            return self.uow.concepts.list(limit=limit, offset=offset, q=q)
