from datetime import datetime, timezone
from uuid import uuid4

import pytest

from ascend.application.captures.delete_capture import DeleteCaptureUseCase
from ascend.application.relationships.create_relationship import CreateRelationshipUseCase
from ascend.domain.captures.entity import Capture
from ascend.domain.relationships.entity import CreatorType, EntityType, RelationshipType
from ascend.infrastructure.events.bus import EventBus
from ascend.infrastructure.uow import SqlAlchemyUnitOfWork


def test_cannot_delete_entity_with_relationships(db_session):
    bus = EventBus()
    uow = SqlAlchemyUnitOfWork(db_session, bus)

    id1 = uuid4()
    id2 = uuid4()

    with uow:
        uow.captures.save(Capture(id=id1, content="C1", created_at=datetime.now(timezone.utc)))
        uow.captures.save(Capture(id=id2, content="C2", created_at=datetime.now(timezone.utc)))
        uow.commit()

    rel_use_case = CreateRelationshipUseCase(uow)
    rel_use_case.execute(
        relationship_id=uuid4(),
        from_id=id1,
        from_type=EntityType.CAPTURE,
        to_id=id2,
        to_type=EntityType.CAPTURE,
        relationship_type=RelationshipType.RELATED_TO,
        confidence=1.0,
        created_by=CreatorType.SYSTEM,
    )

    from ascend.domain.exceptions import ConflictError
    del_use_case = DeleteCaptureUseCase(uow)
    with pytest.raises(ConflictError, match="Cannot delete capture with existing relationships."):
        del_use_case.execute(id1)

    with pytest.raises(ConflictError, match="Cannot delete capture with existing relationships."):
        del_use_case.execute(id2)
