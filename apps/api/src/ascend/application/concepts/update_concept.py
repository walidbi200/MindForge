from datetime import datetime, timezone
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.exceptions import NotFoundError
from ascend.domain.concepts.entity import Concept
from ascend.domain.events.concept_events import ConceptUpdated


class UpdateConceptUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, concept_id: UUID, title: str | None = None, summary: str | None = None) -> Concept:
        with self.uow:
            concept = self.uow.concepts.get(concept_id)
            if not concept:
                raise NotFoundError(f"Concept with id {concept_id} not found")

            updated = False
            if title is not None and concept.title != title:
                concept.title = title
                updated = True
            
            if summary is not None and concept.summary != summary:
                concept.summary = summary
                updated = True
                
            if updated:
                concept.updated_at = datetime.now(timezone.utc)
                self.uow.concepts.save(concept)
                self.uow.emit(ConceptUpdated(aggregate_id=concept.id))

            self.uow.commit()

        return concept
