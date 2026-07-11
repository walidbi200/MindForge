from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.captures.entity import Capture
from ascend.domain.events.capture_events import CaptureUpdated


class UpdateCaptureUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, capture_id: UUID, content: str) -> Capture | None:
        with self.uow:
            capture = self.uow.captures.get(capture_id)
            if not capture:
                return None

            capture.content = content
            self.uow.captures.save(capture)
            self.uow.emit(CaptureUpdated(aggregate_id=capture.id, content=capture.content))
            self.uow.commit()

        return capture
