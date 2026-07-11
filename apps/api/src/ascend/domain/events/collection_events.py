from dataclasses import dataclass, field

from ascend.domain.events.base import DomainEvent
from ascend.domain.relationships.entity import EntityType


@dataclass(frozen=True)
class CollectionCreated(DomainEvent):
    aggregate_type: str = field(default="Collection", init=False)
    event_type: str = field(default="CollectionCreated", init=False)
    name: str = ""


@dataclass(frozen=True)
class CollectionUpdated(DomainEvent):
    aggregate_type: str = field(default="Collection", init=False)
    event_type: str = field(default="CollectionUpdated", init=False)
    name: str = ""


@dataclass(frozen=True)
class CollectionDeleted(DomainEvent):
    aggregate_type: str = field(default="Collection", init=False)
    event_type: str = field(default="CollectionDeleted", init=False)


@dataclass(frozen=True)
class EntityAddedToCollection(DomainEvent):
    aggregate_type: str = field(default="Collection", init=False)
    event_type: str = field(default="EntityAddedToCollection", init=False)
    entity_id: str = ""
    entity_type: EntityType = EntityType.CAPTURE


@dataclass(frozen=True)
class EntityRemovedFromCollection(DomainEvent):
    aggregate_type: str = field(default="Collection", init=False)
    event_type: str = field(default="EntityRemovedFromCollection", init=False)
    entity_id: str = ""
    entity_type: EntityType = EntityType.CAPTURE
