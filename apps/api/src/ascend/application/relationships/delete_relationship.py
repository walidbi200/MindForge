from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.events.relationship_events import RelationshipDeleted


class DeleteRelationshipUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, relationship_id: UUID) -> bool:
        with self.uow:
            relationship = self.uow.relationships.get(relationship_id)
            if not relationship:
                return False

            self.uow.relationships.delete(relationship_id)

            event = RelationshipDeleted(
                aggregate_id=relationship.id,
                from_id=str(relationship.from_id),
                from_type=relationship.from_type,
                to_id=str(relationship.to_id),
                to_type=relationship.to_type,
                relationship_type=relationship.relationship_type,
            )
            self.uow.emit(event)
            self.uow.commit()

        return True
