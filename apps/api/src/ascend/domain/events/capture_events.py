from dataclasses import dataclass, field

from ascend.domain.events.base import DomainEvent


@dataclass(frozen=True)
class CaptureCreated(DomainEvent):
    aggregate_type: str = field(default="Capture", init=False)
    event_type: str = field(default="CaptureCreated", init=False)
    content: str = ""


@dataclass(frozen=True)
class CaptureUpdated(DomainEvent):
    aggregate_type: str = field(default="Capture", init=False)
    event_type: str = field(default="CaptureUpdated", init=False)
    content: str = ""


@dataclass(frozen=True)
class CaptureDeleted(DomainEvent):
    aggregate_type: str = field(default="Capture", init=False)
    event_type: str = field(default="CaptureDeleted", init=False)
