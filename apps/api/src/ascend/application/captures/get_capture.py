from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.captures.entity import Capture


class GetCaptureUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, capture_id: UUID) -> Capture | None:
        with self.uow:
            return self.uow.captures.get(capture_id)
