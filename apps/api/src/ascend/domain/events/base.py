import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    aggregate_id: UUID
    aggregate_type: str
    event_type: str
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: UUID | None = None
    version: int = 1

    def to_dict(self) -> dict:
        """Serialize the event to a dictionary."""
        data = asdict(self)
        # Convert UUIDs and datetimes to strings for JSON serialization
        for key, value in data.items():
            if isinstance(value, UUID):
                data[key] = str(value)
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

    def to_json(self) -> str:
        """Serialize the event to a JSON string."""
        return json.dumps(self.to_dict())
