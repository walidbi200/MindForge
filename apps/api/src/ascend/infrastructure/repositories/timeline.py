from sqlmodel import Session, select

from ascend.domain.events.base import DomainEvent
from ascend.infrastructure.models.timeline_event import TimelineEventModel


class TimelineRepository:
    def __init__(self, session: Session):
        self.session = session

    def append(self, event: DomainEvent) -> None:
        model = TimelineEventModel(
            id=event.event_id,
            aggregate_id=event.aggregate_id,
            aggregate_type=event.aggregate_type,
            event_type=event.event_type,
            payload_json=event.to_json(),
            occurred_at=event.occurred_at,
            correlation_id=event.correlation_id,
            version=event.version,
        )
        self.session.add(model)

    def list(self, limit: int = 50, offset: int = 0) -> list[TimelineEventModel]:
        statement = (
            select(TimelineEventModel).order_by(TimelineEventModel.occurred_at.desc()).offset(offset).limit(limit)
        )
        results = self.session.exec(statement).all()
        return list(results)
