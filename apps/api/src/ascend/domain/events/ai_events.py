from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from ascend.domain.events.base import DomainEvent


@dataclass(frozen=True, kw_only=True)
class AIAnalysisRequested(DomainEvent):
    aggregate_type: str = field(default="Capture", init=False)
    event_type: str = field(default="AIAnalysisRequested", init=False)
    aggregate_id: UUID
    provider: str
    model: str
    metadata: dict[str, Any]


@dataclass(frozen=True, kw_only=True)
class AIAnalysisCompleted(DomainEvent):
    aggregate_type: str = field(default="Capture", init=False)
    event_type: str = field(default="AIAnalysisCompleted", init=False)
    aggregate_id: UUID
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
    metadata: dict[str, Any]


@dataclass(frozen=True, kw_only=True)
class AIAnalysisFailed(DomainEvent):
    aggregate_type: str = field(default="Capture", init=False)
    event_type: str = field(default="AIAnalysisFailed", init=False)
    aggregate_id: UUID
    provider: str
    model: str
    error_message: str
    metadata: dict[str, Any]
