from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.events.collection_events import EntityRemovedFromCollection


class RemoveEntityFromCollectionUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, collection_id: UUID, entity_id: UUID) -> bool:
        with self.uow:
            membership = self.uow.memberships.find(collection_id, entity_id)
            if not membership:
                return False

            self.uow.memberships.delete(membership.id)
            self.uow.emit(
                EntityRemovedFromCollection(
                    aggregate_id=collection_id,
                    entity_id=str(entity_id),
                    entity_type=membership.entity_type,
                )
            )
            self.uow.commit()

        return True
