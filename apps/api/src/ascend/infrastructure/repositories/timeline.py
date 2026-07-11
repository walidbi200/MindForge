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

    def list(
        self,
        limit: int = 50,
        offset: int = 0,
        aggregate_type: str | None = None,
        event_type: str | None = None,
    ) -> "list[TimelineEventModel]":
        statement = select(TimelineEventModel)
        if aggregate_type:
            statement = statement.where(TimelineEventModel.aggregate_type == aggregate_type)
        if event_type:
            statement = statement.where(TimelineEventModel.event_type == event_type)
        statement = statement.order_by(TimelineEventModel.occurred_at.desc()).offset(offset).limit(limit)
        results = self.session.exec(statement).all()
        return list(results)

    def list_by_event_type(self, event_type: str, limit: int = 50, offset: int = 0) -> "list[TimelineEventModel]":
        statement = (
            select(TimelineEventModel)
            .where(TimelineEventModel.event_type == event_type)
            .order_by(TimelineEventModel.occurred_at.desc())
            .offset(offset)
            .limit(limit)
        )
        results = self.session.exec(statement).all()
        return list(results)
