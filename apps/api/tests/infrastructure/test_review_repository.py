"""Tests for SqlAlchemyReviewRepository."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from ascend.domain.relationships.entity import EntityType
from ascend.domain.reviews.entity import Difficulty, Review, ReviewStatus, ReviewType
from ascend.infrastructure.repositories.review import SqlAlchemyReviewRepository


def _make_review(
    entity_id=None,
    entity_type=EntityType.CAPTURE,
    review_type=ReviewType.RECALL,
    status=ReviewStatus.NEW,
    difficulty=Difficulty.MEDIUM,
    next_review_at=None,
) -> Review:
    now = datetime.now(timezone.utc)
    return Review(
        id=uuid4(),
        entity_id=entity_id or uuid4(),
        entity_type=entity_type,
        review_type=review_type,
        status=status,
        difficulty=difficulty,
        score=0,
        notes="",
        created_at=now,
        updated_at=now,
        last_reviewed_at=None,
        next_review_at=next_review_at,
    )


def test_save_and_get(db_session):
    repo = SqlAlchemyReviewRepository(db_session)
    review = _make_review()
    repo.save(review)
    db_session.flush()

    fetched = repo.get(review.id)
    assert fetched is not None
    assert fetched.id == review.id
    assert fetched.entity_type == EntityType.CAPTURE
    assert fetched.review_type == ReviewType.RECALL
    assert fetched.status == ReviewStatus.NEW


def test_get_not_found(db_session):
    repo = SqlAlchemyReviewRepository(db_session)
    assert repo.get(uuid4()) is None


def test_save_updates_existing(db_session):
    repo = SqlAlchemyReviewRepository(db_session)
    review = _make_review()
    repo.save(review)
    db_session.flush()

    # Update the review
    review.score = 4
    review.status = ReviewStatus.REVIEWING
    repo.save(review)
    db_session.flush()

    fetched = repo.get(review.id)
    assert fetched.score == 4
    assert fetched.status == ReviewStatus.REVIEWING


def test_delete(db_session):
    repo = SqlAlchemyReviewRepository(db_session)
    review = _make_review()
    repo.save(review)
    db_session.flush()

    repo.delete(review.id)
    db_session.flush()

    assert repo.get(review.id) is None


def test_list(db_session):
    repo = SqlAlchemyReviewRepository(db_session)
    entity_id = uuid4()
    r1 = _make_review(entity_id=entity_id, review_type=ReviewType.RECALL)
    r2 = _make_review(review_type=ReviewType.READ)
    repo.save(r1)
    repo.save(r2)
    db_session.flush()

    all_reviews = repo.list()
    ids = [r.id for r in all_reviews]
    assert r1.id in ids
    assert r2.id in ids


def test_list_by_entity(db_session):
    repo = SqlAlchemyReviewRepository(db_session)
    entity_id = uuid4()
    r1 = _make_review(entity_id=entity_id)
    r2 = _make_review()  # different entity
    repo.save(r1)
    repo.save(r2)
    db_session.flush()

    entity_reviews = repo.list_by_entity(entity_id)
    assert len(entity_reviews) == 1
    assert entity_reviews[0].id == r1.id


def test_list_due_reviews(db_session):
    repo = SqlAlchemyReviewRepository(db_session)
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=1)
    future = now + timedelta(days=1)

    due_review = _make_review(next_review_at=past)
    not_due_review = _make_review(next_review_at=future)
    no_schedule_review = _make_review()  # next_review_at = None

    repo.save(due_review)
    repo.save(not_due_review)
    repo.save(no_schedule_review)
    db_session.flush()

    due = repo.list_due_reviews()
    due_ids = [r.id for r in due]
    assert due_review.id in due_ids
    assert not_due_review.id not in due_ids
    assert no_schedule_review.id not in due_ids


def test_find_active_by_entity_and_type(db_session):
    repo = SqlAlchemyReviewRepository(db_session)
    entity_id = uuid4()
    review = _make_review(entity_id=entity_id, review_type=ReviewType.FLASHCARD)
    repo.save(review)
    db_session.flush()

    found = repo.find_active_by_entity_and_type(entity_id, ReviewType.FLASHCARD)
    assert found is not None
    assert found.id == review.id

    not_found = repo.find_active_by_entity_and_type(entity_id, ReviewType.QUIZ)
    assert not_found is None
