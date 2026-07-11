from uuid import UUID

from ascend.application.collections.helpers import cleanup_entity_memberships
from ascend.application.uow import UnitOfWork
from ascend.domain.events.capture_events import CaptureDeleted


class DeleteCaptureUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, capture_id: UUID) -> bool:
        with self.uow:
            capture = self.uow.captures.get(capture_id)
            if not capture:
                return False

            if self.uow.relationships.list_incoming(capture_id) or self.uow.relationships.list_outgoing(capture_id):
                raise ValueError("Cannot delete capture with existing relationships.")

            cleanup_entity_memberships(self.uow, capture_id)
            self.uow.captures.delete(capture_id)
            self.uow.emit(CaptureDeleted(aggregate_id=capture_id))
            self.uow.commit()

        return True
