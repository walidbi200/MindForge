from ascend.application.uow import UnitOfWork
from ascend.domain.captures.entity import Capture


class ListCapturesUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, limit: int = 50, offset: int = 0, q: str | None = None) -> list[Capture]:
        with self.uow:
            return self.uow.captures.list(limit=limit, offset=offset, q=q)
