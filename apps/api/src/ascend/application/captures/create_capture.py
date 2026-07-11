from datetime import datetime, timezone
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.captures.entity import Capture
from ascend.domain.events.capture_events import CaptureCreated


class CreateCaptureUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, capture_id: UUID, content: str) -> Capture:
        now = datetime.now(timezone.utc)
        capture = Capture(id=capture_id, content=content, created_at=now)

        with self.uow:
            self.uow.captures.save(capture)
            self.uow.emit(CaptureCreated(aggregate_id=capture.id, content=capture.content))
            self.uow.commit()

        return capture
