from datetime import datetime, timezone
from uuid import uuid4

import pytest

from ascend.application.relationships.create_relationship import CreateRelationshipUseCase
from ascend.domain.captures.entity import Capture
from ascend.domain.exceptions import ConflictError, EntityNotFoundError, ValidationError
from ascend.domain.relationships.entity import CreatorType, EntityType, RelationshipType
from ascend.infrastructure.events.bus import EventBus
from ascend.infrastructure.uow import SqlAlchemyUnitOfWork


def test_create_relationship_validation(db_session):
    bus = EventBus()
    uow = SqlAlchemyUnitOfWork(db_session, bus)
    use_case = CreateRelationshipUseCase(uow)

    id1 = uuid4()
    id2 = uuid4()

    # 1. Self links not allowed
    with pytest.raises(ValidationError, match="Self-links are not allowed"):
        use_case.execute(
            relationship_id=uuid4(),
            from_id=id1,
            from_type=EntityType.CAPTURE,
            to_id=id1,
            to_type=EntityType.CAPTURE,
            relationship_type=RelationshipType.RELATED_TO,
            confidence=1.0,
            created_by=CreatorType.SYSTEM,
        )

    # 2. Entity existence check
    with pytest.raises(EntityNotFoundError, match="Capture .* does not exist."):
        use_case.execute(
            relationship_id=uuid4(),
            from_id=id1,
            from_type=EntityType.CAPTURE,
            to_id=id2,
            to_type=EntityType.CAPTURE,
            relationship_type=RelationshipType.RELATED_TO,
            confidence=1.0,
            created_by=CreatorType.SYSTEM,
        )

    # 3. Create dummy entities for duplicate test
    with uow:
        uow.captures.save(Capture(id=id1, content="C1", created_at=datetime.now(timezone.utc)))
        uow.captures.save(Capture(id=id2, content="C2", created_at=datetime.now(timezone.utc)))
        uow.commit()

    # Create first relationship
    use_case.execute(
        relationship_id=uuid4(),
        from_id=id1,
        from_type=EntityType.CAPTURE,
        to_id=id2,
        to_type=EntityType.CAPTURE,
        relationship_type=RelationshipType.RELATED_TO,
        confidence=1.0,
        created_by=CreatorType.SYSTEM,
    )

    # 4. Duplicate relationships not allowed
    with pytest.raises(ConflictError, match="Duplicate relationship."):
        use_case.execute(
            relationship_id=uuid4(),
            from_id=id1,
            from_type=EntityType.CAPTURE,
            to_id=id2,
            to_type=EntityType.CAPTURE,
            relationship_type=RelationshipType.RELATED_TO,
            confidence=1.0,
            created_by=CreatorType.SYSTEM,
        )
