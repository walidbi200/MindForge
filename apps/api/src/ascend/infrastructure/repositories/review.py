from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlmodel import Session, select

from ascend.domain.reviews.entity import Review, ReviewStatus
from ascend.domain.reviews.repository import ReviewRepository
from ascend.infrastructure.models.review import ReviewModel


class SqlAlchemyReviewRepository(ReviewRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_domain(self, model: ReviewModel) -> Review:
        return Review(
            id=model.id,
            entity_id=model.entity_id,
            entity_type=model.entity_type,
            due_at=model.due_at,
            completed_at=model.completed_at,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
            metadata_json=model.metadata_json,
        )

    def _to_model(self, entity: Review) -> ReviewModel:
        return ReviewModel(
            id=entity.id,
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            due_at=entity.due_at,
            completed_at=entity.completed_at,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            metadata_json=entity.metadata_json,
        )

    def save(self, review: Review) -> None:
        model = self._to_model(review)
        self.session.merge(model)

    def get(self, review_id: UUID) -> Review | None:
        model = self.session.get(ReviewModel, review_id)
        return self._to_domain(model) if model else None

    def delete(self, review_id: UUID) -> None:
        model = self.session.get(ReviewModel, review_id)
        if model:
            self.session.delete(model)

    def list(self) -> list[Review]:
        statement = select(ReviewModel)
        results = self.session.exec(statement).all()
        return [self._to_domain(r) for r in results]

    def list_due(self, as_of: datetime) -> list[Review]:
        statement = select(ReviewModel).where(
            ReviewModel.status == ReviewStatus.PENDING,
            ReviewModel.due_at <= as_of
        )
        results = self.session.exec(statement).all()
        return [self._to_domain(r) for r in results]

    def list_by_entity(self, entity_id: UUID) -> list[Review]:
        statement = select(ReviewModel).where(ReviewModel.entity_id == entity_id)
        results = self.session.exec(statement).all()
        return [self._to_domain(r) for r in results]
