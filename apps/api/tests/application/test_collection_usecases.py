from datetime import datetime, timezone
from uuid import uuid4

import pytest

from ascend.application.captures.delete_capture import DeleteCaptureUseCase
from ascend.application.collections.add_entity_to_collection import AddEntityToCollectionUseCase
from ascend.application.collections.create_collection import CreateCollectionUseCase
from ascend.application.collections.delete_collection import DeleteCollectionUseCase
from ascend.application.collections.list_collection_entities import ListCollectionEntitiesUseCase
from ascend.application.collections.list_collections import ListCollectionsUseCase
from ascend.application.collections.list_entity_collections import ListEntityCollectionsUseCase
from ascend.application.collections.remove_entity_from_collection import RemoveEntityFromCollectionUseCase
from ascend.application.collections.update_collection import UpdateCollectionUseCase
from ascend.domain.captures.entity import Capture
from ascend.domain.relationships.entity import EntityType
from ascend.infrastructure.events.bus import EventBus
from ascend.infrastructure.repositories.timeline import TimelineRepository
from ascend.infrastructure.uow import SqlAlchemyUnitOfWork


def test_collection_usecases_lifecycle(db_session):
    bus = EventBus()
    uow = SqlAlchemyUnitOfWork(db_session, bus)
    timeline_repo = TimelineRepository(db_session)

    create_uc = CreateCollectionUseCase(uow)
    update_uc = UpdateCollectionUseCase(uow)
    delete_uc = DeleteCollectionUseCase(uow)
    list_uc = ListCollectionsUseCase(uow)

    col_id = uuid4()

    # 1. Create Collection
    col = create_uc.execute(collection_id=col_id, name="Networking")
    assert col.name == "Networking"

    # Verify event
    events = timeline_repo.list()
    assert any(e.event_type == "CollectionCreated" and e.aggregate_id == col_id for e in events)

    # 2. Duplicate Name validation
    with pytest.raises(ValueError, match="already exists"):
        create_uc.execute(collection_id=uuid4(), name="Networking")

    # 3. Update Collection
    updated = update_uc.execute(collection_id=col_id, name="Advanced Networking")
    assert updated.name == "Advanced Networking"

    # Verify event
    events = timeline_repo.list()
    assert any(e.event_type == "CollectionUpdated" and e.aggregate_id == col_id for e in events)

    # 4. List Collections
    collections = list_uc.execute()
    assert any(c.id == col_id for c in collections)

    # 5. Delete Empty Collection
    success = delete_uc.execute(col_id)
    assert success is True

    # Verify event
    events = timeline_repo.list()
    assert any(e.event_type == "CollectionDeleted" and e.aggregate_id == col_id for e in events)


def test_membership_usecases(db_session):
    bus = EventBus()
    uow = SqlAlchemyUnitOfWork(db_session, bus)
    timeline_repo = TimelineRepository(db_session)

    create_col_uc = CreateCollectionUseCase(uow)
    delete_col_uc = DeleteCollectionUseCase(uow)
    add_member_uc = AddEntityToCollectionUseCase(uow)
    remove_member_uc = RemoveEntityFromCollectionUseCase(uow)
    list_entities_uc = ListCollectionEntitiesUseCase(uow)
    list_cols_uc = ListEntityCollectionsUseCase(uow)

    col_id = uuid4()
    create_col_uc.execute(collection_id=col_id, name="Linux")

    # Save a Capture
    cap_id = uuid4()
    with uow:
        uow.captures.save(Capture(id=cap_id, content="Linux details", created_at=datetime.now(timezone.utc)))
        uow.commit()

    # 1. Add Capture to Collection
    add_member_uc.execute(uuid4(), col_id, cap_id, EntityType.CAPTURE)

    # Verify event
    events = timeline_repo.list()
    assert any(e.event_type == "EntityAddedToCollection" and e.aggregate_id == col_id for e in events)

    # 2. Duplicate membership error
    with pytest.raises(ValueError, match="already a member"):
        add_member_uc.execute(uuid4(), col_id, cap_id, EntityType.CAPTURE)

    # 3. Deletion blocked on non-empty collection
    with pytest.raises(ValueError, match="active memberships"):
        delete_col_uc.execute(col_id)

    # 4. List entities and collections
    members = list_entities_uc.execute(col_id)
    assert len(members) == 1
    assert members[0].id == cap_id

    member_cols = list_cols_uc.execute(cap_id)
    assert len(member_cols) == 1
    assert member_cols[0].id == col_id

    # 5. Remove member
    success = remove_member_uc.execute(col_id, cap_id)
    assert success is True

    # Verify event
    events = timeline_repo.list()
    assert any(e.event_type == "EntityRemovedFromCollection" and e.aggregate_id == col_id for e in events)


def test_cascade_delete_memberships(db_session):
    bus = EventBus()
    uow = SqlAlchemyUnitOfWork(db_session, bus)

    create_col_uc = CreateCollectionUseCase(uow)
    add_member_uc = AddEntityToCollectionUseCase(uow)
    delete_capture_uc = DeleteCaptureUseCase(uow)

    col_id = uuid4()
    create_col_uc.execute(collection_id=col_id, name="Cloud")

    cap_id = uuid4()
    with uow:
        uow.captures.save(Capture(id=cap_id, content="Cloud stuff", created_at=datetime.now(timezone.utc)))
        uow.commit()

    # Add Capture to Collection
    add_member_uc.execute(uuid4(), col_id, cap_id, EntityType.CAPTURE)

    # Verify membership exists
    with uow:
        assert uow.memberships.find(col_id, cap_id) is not None

    # Delete Capture
    delete_capture_uc.execute(cap_id)

    # Verify membership deleted
    with uow:
        assert uow.memberships.find(col_id, cap_id) is None
