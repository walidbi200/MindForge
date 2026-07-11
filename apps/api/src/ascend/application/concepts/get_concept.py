from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.concepts.entity import Concept


class GetConceptUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, concept_id: UUID) -> Concept | None:
        with self.uow:
            return self.uow.concepts.get(concept_id)
