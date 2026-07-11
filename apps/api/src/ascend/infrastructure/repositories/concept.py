from uuid import UUID

from sqlmodel import Session

from ascend.domain.concepts.entity import Concept
from ascend.domain.concepts.repository import ConceptRepository
from ascend.infrastructure.models.concept import ConceptModel


class SqlAlchemyConceptRepository(ConceptRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, concept: Concept) -> None:
        model = ConceptModel(
            id=concept.id,
            title=concept.title,
            summary=concept.summary,
            created_at=concept.created_at,
            updated_at=concept.updated_at,
        )
        self.session.add(model)

    def get(self, concept_id: UUID) -> Concept | None:
        model = self.session.get(ConceptModel, concept_id)
        if not model:
            return None
        return Concept(
            id=model.id,
            title=model.title,
            summary=model.summary,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def delete(self, concept_id: UUID) -> None:
        model = self.session.get(ConceptModel, concept_id)
        if model:
            self.session.delete(model)

    def list(self, limit: int = 50, offset: int = 0, q: str | None = None) -> list[Concept]:
        from sqlmodel import select

        query = select(ConceptModel)
        if q:
            query = query.where(ConceptModel.title.ilike(f"%{q}%"))

        models = self.session.exec(query.order_by(ConceptModel.created_at.desc()).offset(offset).limit(limit)).all()
        return [
            Concept(
                id=model.id,
                title=model.title,
                summary=model.summary,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )
            for model in models
        ]

    def list_by_ids(self, ids: "list[UUID]") -> "list[Concept]":
        if not ids:
            return []
        from sqlmodel import select

        statement = select(ConceptModel).where(ConceptModel.id.in_(ids))
        models = self.session.exec(statement).all()
        return [
            Concept(
                id=model.id,
                title=model.title,
                summary=model.summary,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )
            for model in models
        ]
