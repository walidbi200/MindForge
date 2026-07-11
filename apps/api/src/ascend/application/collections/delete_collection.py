from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.events.collection_events import CollectionDeleted
from ascend.domain.exceptions import CollectionNotEmptyError


class DeleteCollectionUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, collection_id: UUID) -> bool:
        with self.uow:
            collection = self.uow.collections.get(collection_id)
            if not collection:
                return False

            memberships = self.uow.memberships.list_by_collection(collection_id)
            if memberships:
                raise CollectionNotEmptyError("Cannot delete collection with active memberships.")

            self.uow.collections.delete(collection_id)
            self.uow.emit(CollectionDeleted(aggregate_id=collection_id))
            self.uow.commit()

        return True
