"""Tests for Review use cases."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from ascend.application.reviews.complete_review import CompleteReviewUseCase
from ascend.application.reviews.create_review import CreateReviewUseCase
from ascend.application.reviews.delete_review import DeleteReviewUseCase
from ascend.application.reviews.get_review import GetReviewUseCase
from ascend.application.reviews.list_due_reviews import ListDueReviewsUseCase
from ascend.application.reviews.list_reviews import ListReviewsUseCase
from ascend.application.reviews.update_review import UpdateReviewUseCase
from ascend.domain.captures.entity import Capture
from ascend.domain.relationships.entity import EntityType
from ascend.domain.reviews.entity import Difficulty, ReviewStatus, ReviewType
from ascend.infrastructure.events.bus import EventBus
from ascend.infrastructure.repositories.capture import SqlAlchemyCaptureRepository
from ascend.infrastructure.repositories.review import SqlAlchemyReviewRepository
from ascend.infrastructure.uow import SqlAlchemyUnitOfWork


def _make_uow(db_session):
    return SqlAlchemyUnitOfWork(session=db_session, bus=EventBus())


def _create_capture(db_session) -> Capture:
    """Helper: create a Capture so CreateReviewUseCase can validate entity existence."""
    now = datetime.now(timezone.utc)
    capture = Capture(
        id=uuid4(),
        content="Some content for review testing",
        created_at=now,
    )
    repo = SqlAlchemyCaptureRepository(db_session)
    repo.save(capture)
    db_session.flush()
    return capture


class TestCreateReviewUseCase:
    def test_create_review_success(self, db_session):
        capture = _create_capture(db_session)
        uow = _make_uow(db_session)
        use_case = CreateReviewUseCase(uow)

        review = use_case.execute(
            review_id=uuid4(),
            entity_id=capture.id,
            entity_type=EntityType.CAPTURE,
            review_type=ReviewType.RECALL,
            difficulty=Difficulty.MEDIUM,
            notes="First review",
        )

        assert review is not None
        assert review.entity_id == capture.id
        assert review.entity_type == EntityType.CAPTURE
        assert review.review_type == ReviewType.RECALL
        assert review.status == ReviewStatus.NEW
        assert review.notes == "First review"

    def test_create_review_duplicate_raises(self, db_session):
        capture = _create_capture(db_session)
        uow = _make_uow(db_session)
        use_case = CreateReviewUseCase(uow)

        use_case.execute(
            review_id=uuid4(),
            entity_id=capture.id,
            entity_type=EntityType.CAPTURE,
            review_type=ReviewType.RECALL,
            difficulty=Difficulty.MEDIUM,
            notes="",
        )

        with pytest.raises(ValueError, match="already exists"):
            use_case.execute(
                review_id=uuid4(),
                entity_id=capture.id,
                entity_type=EntityType.CAPTURE,
                review_type=ReviewType.RECALL,
                difficulty=Difficulty.MEDIUM,
                notes="",
            )

    def test_create_review_unknown_entity_raises(self, db_session):
        uow = _make_uow(db_session)
        use_case = CreateReviewUseCase(uow)

        with pytest.raises(ValueError, match="does not exist"):
            use_case.execute(
                review_id=uuid4(),
                entity_id=uuid4(),  # non-existent
                entity_type=EntityType.CAPTURE,
                review_type=ReviewType.RECALL,
                difficulty=Difficulty.MEDIUM,
                notes="",
            )


class TestGetReviewUseCase:
    def test_get_existing(self, db_session):
        capture = _create_capture(db_session)
        uow = _make_uow(db_session)
        create_uc = CreateReviewUseCase(uow)
        review = create_uc.execute(
            review_id=uuid4(),
            entity_id=capture.id,
            entity_type=EntityType.CAPTURE,
            review_type=ReviewType.READ,
            difficulty=Difficulty.EASY,
            notes="",
        )

        get_uc = GetReviewUseCase(uow)
        fetched = get_uc.execute(review.id)
        assert fetched is not None
        assert fetched.id == review.id

    def test_get_missing_returns_none(self, db_session):
        uow = _make_uow(db_session)
        get_uc = GetReviewUseCase(uow)
        assert get_uc.execute(uuid4()) is None


class TestCompleteReviewUseCase:
    def test_complete_review(self, db_session):
        capture = _create_capture(db_session)
        uow = _make_uow(db_session)
        create_uc = CreateReviewUseCase(uow)
        review = create_uc.execute(
            review_id=uuid4(),
            entity_id=capture.id,
            entity_type=EntityType.CAPTURE,
            review_type=ReviewType.FLASHCARD,
            difficulty=Difficulty.MEDIUM,
            notes="",
        )

        complete_uc = CompleteReviewUseCase(uow)
        completed = complete_uc.execute(
            review_id=review.id,
            difficulty=Difficulty.EASY,
            score=4,
            notes="Went well",
        )

        assert completed is not None
        assert completed.score == 4
        assert completed.difficulty == Difficulty.EASY
        assert completed.notes == "Went well"
        assert completed.last_reviewed_at is not None
        assert completed.next_review_at is not None
        assert completed.status == ReviewStatus.REVIEWING

    def test_complete_missing_review_returns_none(self, db_session):
        uow = _make_uow(db_session)
        complete_uc = CompleteReviewUseCase(uow)
        result = complete_uc.execute(
            review_id=uuid4(),
            difficulty=Difficulty.MEDIUM,
            score=3,
            notes="",
        )
        assert result is None


class TestUpdateReviewUseCase:
    def test_update_notes_and_status(self, db_session):
        capture = _create_capture(db_session)
        uow = _make_uow(db_session)
        create_uc = CreateReviewUseCase(uow)
        review = create_uc.execute(
            review_id=uuid4(),
            entity_id=capture.id,
            entity_type=EntityType.CAPTURE,
            review_type=ReviewType.QUIZ,
            difficulty=Difficulty.HARD,
            notes="initial",
        )

        update_uc = UpdateReviewUseCase(uow)
        updated = update_uc.execute(
            review_id=review.id,
            notes="updated notes",
            status=ReviewStatus.SUSPENDED,
            difficulty=None,
            score=None,
            next_review_at=None,
        )

        assert updated is not None
        assert updated.notes == "updated notes"
        assert updated.status == ReviewStatus.SUSPENDED


class TestDeleteReviewUseCase:
    def test_delete_review(self, db_session):
        capture = _create_capture(db_session)
        uow = _make_uow(db_session)
        create_uc = CreateReviewUseCase(uow)
        review = create_uc.execute(
            review_id=uuid4(),
            entity_id=capture.id,
            entity_type=EntityType.CAPTURE,
            review_type=ReviewType.RECALL,
            difficulty=Difficulty.MEDIUM,
            notes="",
        )

        delete_uc = DeleteReviewUseCase(uow)
        assert delete_uc.execute(review.id) is True

        get_uc = GetReviewUseCase(uow)
        assert get_uc.execute(review.id) is None

    def test_delete_missing_returns_false(self, db_session):
        uow = _make_uow(db_session)
        delete_uc = DeleteReviewUseCase(uow)
        assert delete_uc.execute(uuid4()) is False


class TestListReviewsUseCases:
    def test_list_all(self, db_session):
        capture = _create_capture(db_session)
        uow = _make_uow(db_session)
        create_uc = CreateReviewUseCase(uow)
        create_uc.execute(
            review_id=uuid4(),
            entity_id=capture.id,
            entity_type=EntityType.CAPTURE,
            review_type=ReviewType.READ,
            difficulty=Difficulty.EASY,
            notes="",
        )

        list_uc = ListReviewsUseCase(uow)
        reviews = list_uc.execute()
        assert len(reviews) >= 1
