from datetime import datetime, timezone
from uuid import uuid4

from ascend.domain.captures.entity import Capture
from ascend.infrastructure.repositories.capture import SqlAlchemyCaptureRepository


def test_save_and_get_capture(db_session):
    repo = SqlAlchemyCaptureRepository(db_session)

    capture_id = uuid4()
    capture = Capture(id=capture_id, content="Test content", created_at=datetime.now(timezone.utc))

    repo.save(capture)
    db_session.commit()

    retrieved = repo.get(capture_id)
    assert retrieved is not None
    assert retrieved.id == capture_id
    assert retrieved.content == "Test content"
