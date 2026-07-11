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
