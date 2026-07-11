from datetime import datetime, timedelta, timezone
from uuid import uuid4

from ascend.domain.relationships.entity import EntityType
from ascend.domain.reviews.entity import Review, ReviewStatus
from ascend.infrastructure.repositories.review import SqlAlchemyReviewRepository


def test_review_repository_crud(db_session):
    repo = SqlAlchemyReviewRepository(db_session)
    rev_id = uuid4()
    ent_id = uuid4()
    now = datetime.now(timezone.utc)
    due = now - timedelta(days=1)

    review = Review(
        id=rev_id,
        entity_id=ent_id,
        entity_type=EntityType.CAPTURE,
        due_at=due,
        completed_at=None,
        status=ReviewStatus.PENDING,
        created_at=now,
        updated_at=now,
    )

    # 1. Save
    repo.save(review)
    db_session.commit()

    # 2. Get
    retrieved = repo.get(rev_id)
    assert retrieved is not None
    assert retrieved.entity_id == ent_id
    assert retrieved.status == ReviewStatus.PENDING

    # 3. List
    assert len(repo.list()) >= 1

    # 4. List Due
    due_reviews = repo.list_due(now)
    assert any(r.id == rev_id for r in due_reviews)

    # 5. List By Entity
    ent_reviews = repo.list_by_entity(ent_id)
    assert len(ent_reviews) == 1
    assert ent_reviews[0].id == rev_id

    # 6. Delete
    repo.delete(rev_id)
    db_session.commit()
    assert repo.get(rev_id) is None
