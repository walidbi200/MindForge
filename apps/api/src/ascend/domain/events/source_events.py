from dataclasses import dataclass, field

from ascend.domain.events.base import DomainEvent
from ascend.domain.sources.entity import SourceType


@dataclass(frozen=True)
class SourceCreated(DomainEvent):
    aggregate_type: str = field(default="Source", init=False)
    event_type: str = field(default="SourceCreated", init=False)
    title: str = ""
    source_type: SourceType = SourceType.MANUAL


@dataclass(frozen=True)
class SourceUpdated(DomainEvent):
    aggregate_type: str = field(default="Source", init=False)
    event_type: str = field(default="SourceUpdated", init=False)
    title: str = ""
    source_type: SourceType = SourceType.MANUAL


@dataclass(frozen=True)
class SourceDeleted(DomainEvent):
    aggregate_type: str = field(default="Source", init=False)
    event_type: str = field(default="SourceDeleted", init=False)
