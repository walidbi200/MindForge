from dataclasses import dataclass, field

from ascend.domain.events.base import DomainEvent


@dataclass(frozen=True)
class ConceptCreated(DomainEvent):
    aggregate_type: str = field(default="Concept", init=False)
    event_type: str = field(default="ConceptCreated", init=False)
    title: str = ""
    summary: str = ""


@dataclass(frozen=True)
class ConceptUpdated(DomainEvent):
    aggregate_type: str = field(default="Concept", init=False)
    event_type: str = field(default="ConceptUpdated", init=False)


@dataclass(frozen=True)
class ConceptDeleted(DomainEvent):
    aggregate_type: str = field(default="Concept", init=False)
    event_type: str = field(default="ConceptDeleted", init=False)


@dataclass(frozen=True)
class ConceptsMerged(DomainEvent):
    aggregate_type: str = field(default="Concept", init=False)
    event_type: str = field(default="ConceptsMerged", init=False)
    source_id: str = ""
    target_id: str = ""
