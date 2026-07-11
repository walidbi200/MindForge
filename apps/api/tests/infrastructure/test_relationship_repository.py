from datetime import datetime, timezone
from uuid import uuid4

from ascend.domain.relationships.entity import CreatorType, EntityType, Relationship, RelationshipType
from ascend.infrastructure.repositories.relationship import SqlAlchemyRelationshipRepository


def test_relationship_repository_crud(db_session):
    repo = SqlAlchemyRelationshipRepository(db_session)

    rel_id = uuid4()
    from_id = uuid4()
    to_id = uuid4()

    relationship = Relationship(
        id=rel_id,
        from_id=from_id,
        from_type=EntityType.CAPTURE,
        to_id=to_id,
        to_type=EntityType.CONCEPT,
        relationship_type=RelationshipType.RELATED_TO,
        confidence=0.8,
        created_by=CreatorType.SYSTEM,
        created_at=datetime.now(timezone.utc),
        metadata_json='{"reason": "test"}',
    )

    repo.save(relationship)
    db_session.commit()

    retrieved = repo.get(rel_id)
    assert retrieved is not None
    assert retrieved.from_id == from_id
    assert retrieved.to_id == to_id
    assert retrieved.confidence == 0.8
    assert retrieved.metadata_json == '{"reason": "test"}'

    # Test outgoing
    outgoing = repo.list_outgoing(from_id)
    assert len(outgoing) == 1
    assert outgoing[0].id == rel_id

    # Test incoming
    incoming = repo.list_incoming(to_id)
    assert len(incoming) == 1
    assert incoming[0].id == rel_id

    # Test delete
    repo.delete(rel_id)
    db_session.commit()
    assert repo.get(rel_id) is None
