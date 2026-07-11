from sqlmodel import Session

from ascend.domain.events.base import DomainEvent
from ascend.infrastructure.repositories.timeline import TimelineRepository


class EventBus:
    """
    Synchronous event bus for MindForge.
    Receives the current active session from the UnitOfWork and persists events.
    """

    def publish(self, events: list[DomainEvent], session: Session) -> None:
        if not events:
            return

        timeline_repo = TimelineRepository(session)
        for event in events:
            timeline_repo.append(event)
