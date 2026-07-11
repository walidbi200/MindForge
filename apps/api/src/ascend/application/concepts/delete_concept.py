from uuid import UUID

from ascend.application.collections.helpers import cleanup_entity_memberships
from ascend.application.uow import UnitOfWork
from ascend.domain.events.concept_events import ConceptDeleted


class DeleteConceptUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, concept_id: UUID) -> bool:
        with self.uow:
            concept = self.uow.concepts.get(concept_id)
            if not concept:
                return False

            if self.uow.relationships.list_incoming(concept_id) or self.uow.relationships.list_outgoing(concept_id):
                from ascend.domain.exceptions import ConflictError
                raise ConflictError("Cannot delete concept with existing relationships.")

            cleanup_entity_memberships(self.uow, concept_id)
            self.uow.concepts.delete(concept_id)
            self.uow.emit(ConceptDeleted(aggregate_id=concept_id))
            self.uow.commit()

        return True
