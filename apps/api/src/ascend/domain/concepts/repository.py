from typing import Protocol
from uuid import UUID

from ascend.domain.concepts.entity import Concept


class ConceptRepository(Protocol):
    def save(self, concept: Concept) -> None: ...

    def get(self, concept_id: UUID) -> Concept | None: ...

    def delete(self, concept_id: UUID) -> None: ...

    def list(self, limit: int = 50, offset: int = 0, q: str | None = None) -> list[Concept]: ...
