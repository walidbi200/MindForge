from typing import Protocol

from ascend.domain.captures.repository import CaptureRepository
from ascend.domain.collections.repository import CollectionRepository, MembershipRepository
from ascend.domain.concepts.repository import ConceptRepository
from ascend.domain.events.base import DomainEvent
from ascend.domain.relationships.repository import RelationshipRepository
from ascend.domain.sources.repository import SourceRepository


class UnitOfWork(Protocol):
    captures: CaptureRepository
    concepts: ConceptRepository
    relationships: RelationshipRepository
    sources: SourceRepository
    collections: CollectionRepository
    memberships: MembershipRepository

    def emit(self, event: DomainEvent) -> None: ...

    def collect_events(self) -> list[DomainEvent]: ...

    def clear_events(self) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...
