from typing import Protocol
from uuid import UUID

from ascend.domain.concepts.entity import Concept


class ConceptRepository(Protocol):
    def save(self, concept: Concept) -> None: ...

    def get(self, concept_id: UUID) -> Concept | None: ...
