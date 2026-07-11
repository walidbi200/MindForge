from datetime import datetime, timezone
from uuid import uuid4

from ascend.domain.collections.entity import Collection, Membership
from ascend.domain.relationships.entity import EntityType
from ascend.infrastructure.repositories.collection import (
    SqlAlchemyCollectionRepository,
    SqlAlchemyMembershipRepository,
)


def test_collection_repository_crud(db_session):
    repo = SqlAlchemyCollectionRepository(db_session)
    col_id = uuid4()
    now = datetime.now(timezone.utc)

    collection = Collection(
        id=col_id,
        name="Test Space",
        description="Space Description",
        color="#3B82F6",
        icon="book",
        created_at=now,
        updated_at=now,
    )

    # 1. Save Collection
    repo.save(collection)
    db_session.commit()

    # 2. Get
    retrieved = repo.get(col_id)
    assert retrieved is not None
    assert retrieved.name == "Test Space"
    assert retrieved.color == "#3B82F6"

    # 3. Get by Name
    retrieved_by_name = repo.get_by_name("Test Space")
    assert retrieved_by_name is not None
    assert retrieved_by_name.id == col_id

    # 4. List
    collections = repo.list()
    assert any(c.id == col_id for c in collections)

    # 5. Delete
    repo.delete(col_id)
    db_session.commit()
    assert repo.get(col_id) is None


def test_membership_repository(db_session):
    repo = SqlAlchemyMembershipRepository(db_session)
    col_id = uuid4()
    entity_id = uuid4()
    mem_id = uuid4()

    membership = Membership(
        id=mem_id,
        collection_id=col_id,
        entity_id=entity_id,
        entity_type=EntityType.CAPTURE,
        created_at=datetime.now(timezone.utc),
    )

    # 1. Save
    repo.save(membership)
    db_session.commit()

    # 2. Get
    retrieved = repo.get(mem_id)
    assert retrieved is not None
    assert retrieved.collection_id == col_id
    assert retrieved.entity_id == entity_id
    assert retrieved.entity_type == EntityType.CAPTURE

    # 3. Find
    found = repo.find(col_id, entity_id)
    assert found is not None
    assert found.id == mem_id

    # 4. List by Collection
    members = repo.list_by_collection(col_id)
    assert len(members) == 1
    assert members[0].id == mem_id

    # 5. List by Entity
    ents = repo.list_by_entity(entity_id)
    assert len(ents) == 1
    assert ents[0].id == mem_id

    # 6. Delete
    repo.delete(mem_id)
    db_session.commit()
    assert repo.get(mem_id) is None

import pytest
from sqlalchemy.exc import IntegrityError


def test_membership_duplicate_protection(db_session):
    repo = SqlAlchemyMembershipRepository(db_session)
    col_id = uuid4()
    entity_id = uuid4()
    
    mem1 = Membership(
        id=uuid4(),
        collection_id=col_id,
        entity_id=entity_id,
        entity_type=EntityType.CAPTURE,
        created_at=datetime.now(timezone.utc),
    )
    repo.save(mem1)
    db_session.commit()
    
    mem2 = Membership(
        id=uuid4(),
        collection_id=col_id,
        entity_id=entity_id,
        entity_type=EntityType.CAPTURE,
        created_at=datetime.now(timezone.utc),
    )
    repo.save(mem2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

def test_membership_cascade_cleanup(db_session):
    repo = SqlAlchemyMembershipRepository(db_session)
    col_id = uuid4()
    entity_id = uuid4()
    
    mem1 = Membership(
        id=uuid4(),
        collection_id=col_id,
        entity_id=entity_id,
        entity_type=EntityType.CAPTURE,
        created_at=datetime.now(timezone.utc),
    )
    repo.save(mem1)
    db_session.commit()
    
    repo.delete_by_entity(entity_id)
    db_session.commit()
    
    assert len(repo.list_by_collection(col_id)) == 0

