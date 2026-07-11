from uuid import uuid4
from datetime import datetime, timezone
from ascend.domain.captures.entity import Capture
from ascend.application.uow import UnitOfWork

class CreateCaptureUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        
    def execute(self, content: str) -> Capture:
        capture = Capture(
            id=uuid4(),
            content=content,
            created_at=datetime.now(timezone.utc)
        )
        with self.uow:
            self.uow.captures.save(capture)
            self.uow.commit()
            
        return capture
