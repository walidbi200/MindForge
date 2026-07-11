from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TimelineEventResponse(BaseModel):
    id: UUID
    aggregate_id: UUID
    aggregate_type: str
    event_type: str
    occurred_at: datetime
    correlation_id: UUID | None = None
    version: int
    payload: dict
