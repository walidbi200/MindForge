from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel


class TimelineEventModel(SQLModel, table=True):
    __tablename__ = "timeline_events"

    id: UUID = Field(primary_key=True)
    aggregate_id: UUID = Field(index=True)
    aggregate_type: str = Field(index=True)
    event_type: str
    payload_json: str
    occurred_at: datetime
    correlation_id: UUID | None = Field(default=None, index=True)
    version: int = Field(default=1)
