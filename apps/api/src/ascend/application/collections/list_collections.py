from ascend.application.uow import UnitOfWork
from ascend.domain.collections.entity import Collection


class ListCollectionsUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(
        self,
        q: str | None = None,
        color: str | None = None,
        icon: str | None = None,
    ) -> list[Collection]:
        with self.uow:
            return self.uow.collections.list(q=q, color=color, icon=icon)
