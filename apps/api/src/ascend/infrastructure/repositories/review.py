from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Session, select

from ascend.domain.reviews.entity import Review
from ascend.domain.reviews.repository import ReviewRepository
from ascend.infrastructure.models.review import ReviewModel


class SqlAlchemyReviewRepository(ReviewRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, review: Review) -> None:
        model = self.session.get(ReviewModel, review.id)
        if model:
            model.status = review.status
            model.difficulty = review.difficulty
            model.score = review.score
            model.notes = review.notes
            model.updated_at = review.updated_at
            model.last_reviewed_at = review.last_reviewed_at
            model.next_review_at = review.next_review_at
        else:
            model = ReviewModel(
                id=review.id,
                entity_id=review.entity_id,
                entity_type=review.entity_type,
                review_type=review.review_type,
                status=review.status,
                difficulty=review.difficulty,
                score=review.score,
                notes=review.notes,
                created_at=review.created_at,
                updated_at=review.updated_at,
                last_reviewed_at=review.last_reviewed_at,
                next_review_at=review.next_review_at,
            )
        self.session.add(model)

    def get(self, review_id: UUID) -> Review | None:
        model = self.session.get(ReviewModel, review_id)
        if not model:
            return None
        return self._to_entity(model)

    def delete(self, review_id: UUID) -> None:
        model = self.session.get(ReviewModel, review_id)
        if model:
            self.session.delete(model)

    def list(self, offset: int = 0, limit: int = 100) -> list[Review]:
        models = self.session.exec(
            select(ReviewModel).offset(offset).limit(limit)
        ).all()
        return [self._to_entity(model) for model in models]

    def list_by_entity(self, entity_id: UUID) -> list[Review]:
        models = self.session.exec(
            select(ReviewModel).where(ReviewModel.entity_id == entity_id)
        ).all()
        return [self._to_entity(model) for model in models]

    def list_due_reviews(self) -> list[Review]:
        now = datetime.now(timezone.utc)
        models = self.session.exec(
            select(ReviewModel)
            .where(ReviewModel.next_review_at <= now)
            .order_by(ReviewModel.next_review_at.asc())
        ).all()
        return [self._to_entity(model) for model in models]

    def find_active_by_entity_and_type(self, entity_id: UUID, review_type: str) -> Review | None:
        model = self.session.exec(
            select(ReviewModel)
            .where(ReviewModel.entity_id == entity_id)
            .where(ReviewModel.review_type == review_type)
        ).first()
        if not model:
            return None
        return self._to_entity(model)

    def _to_entity(self, model: ReviewModel) -> Review:
        return Review(
            id=model.id,
            entity_id=model.entity_id,
            entity_type=model.entity_type,
            review_type=model.review_type,
            status=model.status,
            difficulty=model.difficulty,
            score=model.score,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_reviewed_at=model.last_reviewed_at,
            next_review_at=model.next_review_at,
        )
