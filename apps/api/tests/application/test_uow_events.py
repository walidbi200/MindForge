from uuid import uuid4

from ascend.domain.events.capture_events import CaptureCreated
from ascend.infrastructure.events.bus import EventBus
from ascend.infrastructure.uow import SqlAlchemyUnitOfWork


def test_uow_rollback_clears_events(db_session):
    bus = EventBus()
    uow = SqlAlchemyUnitOfWork(db_session, bus)

    event = CaptureCreated(aggregate_id=uuid4(), content="test")

    with uow:
        uow.emit(event)
        assert len(uow.collect_events()) == 1
        uow.rollback()

    assert len(uow.collect_events()) == 0
