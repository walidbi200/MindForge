from datetime import datetime, timezone
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.concepts.entity import Concept
from ascend.domain.events.concept_events import ConceptCreated


class CreateConceptUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, concept_id: UUID, title: str, summary: str) -> Concept:
        now = datetime.now(timezone.utc)
        concept = Concept(
            id=concept_id,
            title=title,
            summary=summary,
            created_at=now,
            updated_at=now,
        )

        with self.uow:
            self.uow.concepts.save(concept)
            self.uow.emit(ConceptCreated(aggregate_id=concept.id, title=concept.title, summary=concept.summary))
            self.uow.commit()

        return concept
