import json
from uuid import uuid4

from ascend.domain.events.capture_events import CaptureCreated
from ascend.infrastructure.events.bus import EventBus
from ascend.infrastructure.repositories.timeline import TimelineRepository


def test_event_bus_publishes_to_timeline(db_session):
    bus = EventBus()
    repo = TimelineRepository(db_session)

    aggregate_id = uuid4()
    event = CaptureCreated(aggregate_id=aggregate_id, content="test event")

    bus.publish([event], db_session)
    db_session.commit()

    events = repo.list(limit=100)
    found = [e for e in events if e.aggregate_id == aggregate_id]
    assert len(found) == 1
    assert found[0].event_type == "CaptureCreated"

    payload = json.loads(found[0].payload_json)
    assert payload["content"] == "test event"
    assert payload["aggregate_id"] == str(aggregate_id)
