from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.collections.entity import Collection


class ListEntityCollectionsUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, entity_id: UUID) -> list[Collection]:
        collections: list[Collection] = []
        with self.uow:
            memberships = self.uow.memberships.list_by_entity(entity_id)
            for m in memberships:
                collection = self.uow.collections.get(m.collection_id)
                if collection:
                    collections.append(collection)
        return collections
