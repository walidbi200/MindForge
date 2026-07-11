from dataclasses import dataclass, field

from ascend.domain.events.base import DomainEvent
from ascend.domain.relationships.entity import EntityType, RelationshipType


@dataclass(frozen=True)
class RelationshipCreated(DomainEvent):
    aggregate_type: str = field(default="Relationship", init=False)
    event_type: str = field(default="RelationshipCreated", init=False)
    from_id: str = ""
    from_type: EntityType = EntityType.CAPTURE
    to_id: str = ""
    to_type: EntityType = EntityType.CAPTURE
    relationship_type: RelationshipType = RelationshipType.RELATED_TO


@dataclass(frozen=True)
class RelationshipDeleted(DomainEvent):
    aggregate_type: str = field(default="Relationship", init=False)
    event_type: str = field(default="RelationshipDeleted", init=False)
    from_id: str = ""
    from_type: EntityType = EntityType.CAPTURE
    to_id: str = ""
    to_type: EntityType = EntityType.CAPTURE
    relationship_type: RelationshipType = RelationshipType.RELATED_TO
