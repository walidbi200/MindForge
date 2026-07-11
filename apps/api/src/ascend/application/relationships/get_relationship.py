from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.relationships.entity import Relationship


class GetRelationshipUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, relationship_id: UUID) -> Relationship | None:
        with self.uow:
            return self.uow.relationships.get(relationship_id)
