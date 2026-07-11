from sqlmodel import Session

from ascend.application.uow import UnitOfWork
from ascend.domain.events.base import DomainEvent
from ascend.infrastructure.events.bus import EventBus
from ascend.infrastructure.repositories.capture import SqlAlchemyCaptureRepository
from ascend.infrastructure.repositories.collection import SqlAlchemyCollectionRepository, SqlAlchemyMembershipRepository
from ascend.infrastructure.repositories.concept import SqlAlchemyConceptRepository
from ascend.infrastructure.repositories.relationship import SqlAlchemyRelationshipRepository
from ascend.infrastructure.repositories.review import SqlAlchemyReviewRepository
from ascend.infrastructure.repositories.source import SqlAlchemySourceRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: Session, bus: EventBus):
        self.session = session
        self.bus = bus
        self._events: list[DomainEvent] = []
        self.captures = SqlAlchemyCaptureRepository(self.session)
        self.concepts = SqlAlchemyConceptRepository(self.session)
        self.relationships = SqlAlchemyRelationshipRepository(self.session)
        self.sources = SqlAlchemySourceRepository(self.session)
        self.collections = SqlAlchemyCollectionRepository(self.session)
        self.memberships = SqlAlchemyMembershipRepository(self.session)
        self.reviews = SqlAlchemyReviewRepository(self.session)

        from ascend.infrastructure.repositories.timeline import TimelineRepository

        self.timeline = TimelineRepository(self.session)

    def emit(self, event: DomainEvent) -> None:
        self._events.append(event)

    def collect_events(self) -> list[DomainEvent]:
        return list(self._events)

    def clear_events(self) -> None:
        self._events.clear()

    def commit(self) -> None:
        self.session.commit()
        events = self.collect_events()
        if events:
            self.bus.publish(events, self.session)
            self.session.commit()
        self.clear_events()

    def rollback(self) -> None:
        self.session.rollback()
        self.clear_events()

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()
        self.session.close()
