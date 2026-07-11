from dataclasses import dataclass, field

from ascend.domain.events.base import DomainEvent
from ascend.domain.relationships.entity import EntityType
from ascend.domain.reviews.entity import Difficulty


@dataclass(frozen=True)
class ReviewCreated(DomainEvent):
    aggregate_type: str = field(default="Review", init=False)
    event_type: str = field(default="ReviewCreated", init=False)
    entity_id: str = ""
    entity_type: EntityType = EntityType.CAPTURE


@dataclass(frozen=True)
class ReviewUpdated(DomainEvent):
    aggregate_type: str = field(default="Review", init=False)
    event_type: str = field(default="ReviewUpdated", init=False)


@dataclass(frozen=True)
class ReviewDeleted(DomainEvent):
    aggregate_type: str = field(default="Review", init=False)
    event_type: str = field(default="ReviewDeleted", init=False)


@dataclass(frozen=True)
class ReviewCompleted(DomainEvent):
    aggregate_type: str = field(default="Review", init=False)
    event_type: str = field(default="ReviewCompleted", init=False)
    difficulty: Difficulty = Difficulty.MEDIUM
    score: int = 3
