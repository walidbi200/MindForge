from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.relationships.entity import Relationship


class ListOutgoingRelationshipsUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, entity_id: UUID) -> list[Relationship]:
        with self.uow:
            return self.uow.relationships.list_outgoing(entity_id)


class ListIncomingRelationshipsUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, entity_id: UUID) -> list[Relationship]:
        with self.uow:
            return self.uow.relationships.list_incoming(entity_id)
