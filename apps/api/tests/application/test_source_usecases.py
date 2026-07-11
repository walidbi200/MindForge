from datetime import datetime, timezone
from uuid import uuid4

import pytest

from ascend.application.relationships.create_relationship import CreateRelationshipUseCase
from ascend.application.sources.create_source import CreateSourceUseCase
from ascend.application.sources.delete_source import DeleteSourceUseCase
from ascend.application.sources.get_source import GetSourceUseCase
from ascend.application.sources.list_sources import ListSourcesUseCase
from ascend.application.sources.update_source import UpdateSourceUseCase
from ascend.domain.captures.entity import Capture
from ascend.domain.relationships.entity import CreatorType, EntityType, RelationshipType
from ascend.domain.sources.entity import SourceType
from ascend.infrastructure.events.bus import EventBus
from ascend.infrastructure.repositories.timeline import TimelineRepository
from ascend.infrastructure.uow import SqlAlchemyUnitOfWork


def test_source_usecases_lifecycle(db_session):
    bus = EventBus()
    uow = SqlAlchemyUnitOfWork(db_session, bus)

    create_uc = CreateSourceUseCase(uow)
    get_uc = GetSourceUseCase(uow)
    update_uc = UpdateSourceUseCase(uow)
    list_uc = ListSourcesUseCase(uow)
    delete_uc = DeleteSourceUseCase(uow)

    from ascend.domain.exceptions import ValidationError

    # 1. Validation Failures
    with pytest.raises(ValidationError, match="Title is required."):
        create_uc.execute(uuid4(), title=" ", source_type=SourceType.WEB_ARTICLE)

    # 2. Create Source
    sid = uuid4()
    source = create_uc.execute(
        source_id=sid,
        title="My Article",
        source_type=SourceType.WEB_ARTICLE,
        uri="https://example.com",
    )
    assert source.id == sid
    assert source.title == "My Article"
    assert source.source_type == SourceType.WEB_ARTICLE

    # Verify Timeline Event emitted in Database
    timeline_repo = TimelineRepository(db_session)
    events = timeline_repo.list()
    assert any(e.event_type == "SourceCreated" and e.aggregate_id == sid for e in events)

    # 3. Get Source
    retrieved = get_uc.execute(sid)
    assert retrieved is not None
    assert retrieved.title == "My Article"

    # 4. Update Source
    updated = update_uc.execute(sid, title="Updated Article Title", publisher="Publisher X")
    assert updated.title == "Updated Article Title"
    assert updated.publisher == "Publisher X"

    events = timeline_repo.list()
    assert any(e.event_type == "SourceUpdated" and e.aggregate_id == sid for e in events)

    # 5. List Sources
    results = list_uc.execute()
    assert any(s.id == sid for s in results)

    # 6. Deletion Protection (Create Capture and link it)
    cid = uuid4()
    with uow:
        uow.captures.save(Capture(id=cid, content="Capture tied to source", created_at=datetime.now(timezone.utc)))
        uow.commit()

    rel_uc = CreateRelationshipUseCase(uow)
    rel_uc.execute(
        relationship_id=uuid4(),
        from_id=sid,
        from_type=EntityType.SOURCE,
        to_id=cid,
        to_type=EntityType.CAPTURE,
        relationship_type=RelationshipType.DERIVED_FROM,
        confidence=1.0,
        created_by=CreatorType.USER,
    )

    from ascend.domain.exceptions import ConflictError

    # Deletion should fail
    with pytest.raises(ConflictError, match="Cannot delete source with existing relationships."):
        delete_uc.execute(sid)

    # Remove relationship first (simulate delete relationship)
    with uow:
        # Get the relationship we just created to delete it
        rels = uow.relationships.list_outgoing(sid)
        for r in rels:
            uow.relationships.delete(r.id)
        uow.commit()

    # Deletion should now succeed
    success = delete_uc.execute(sid)
    assert success is True
    assert get_uc.execute(sid) is None
