from datetime import datetime, timezone
from uuid import uuid4

from ascend.domain.concepts.entity import Concept
from ascend.infrastructure.repositories.concept import SqlAlchemyConceptRepository


def test_save_and_get_concept(db_session):
    repo = SqlAlchemyConceptRepository(db_session)

    concept_id = uuid4()
    now = datetime.now(timezone.utc)
    concept = Concept(
        id=concept_id,
        title="Test Concept",
        summary="A test summary of knowledge.",
        created_at=now,
        updated_at=now,
    )

    repo.save(concept)
    db_session.commit()

    retrieved = repo.get(concept_id)
    assert retrieved is not None
    assert retrieved.id == concept_id
    assert retrieved.title == "Test Concept"
    assert retrieved.summary == "A test summary of knowledge."
