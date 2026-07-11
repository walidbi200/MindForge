from uuid import UUID

from ascend.application.collections.helpers import cleanup_entity_memberships
from ascend.application.uow import UnitOfWork
from ascend.domain.events.source_events import SourceDeleted
from ascend.domain.exceptions import ConflictError


class DeleteSourceUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, source_id: UUID) -> bool:
        with self.uow:
            source = self.uow.sources.get(source_id)
            if not source:
                return False

            if self.uow.relationships.list_incoming(source_id) or self.uow.relationships.list_outgoing(source_id):
                raise ConflictError("Cannot delete source with existing relationships.")

            cleanup_entity_memberships(self.uow, source_id)
            self.uow.sources.delete(source_id)
            self.uow.emit(SourceDeleted(aggregate_id=source_id))
            self.uow.commit()

        return True
