from uuid import UUID

from sqlmodel import Session, select

from ascend.domain.relationships.entity import Relationship, RelationshipType
from ascend.domain.relationships.repository import RelationshipRepository
from ascend.infrastructure.models.relationship import RelationshipModel


class SqlAlchemyRelationshipRepository(RelationshipRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, relationship: Relationship) -> None:
        model = RelationshipModel(
            id=relationship.id,
            from_id=relationship.from_id,
            from_type=relationship.from_type,
            to_id=relationship.to_id,
            to_type=relationship.to_type,
            relationship_type=relationship.relationship_type,
            confidence=relationship.confidence,
            created_by=relationship.created_by,
            created_at=relationship.created_at,
            metadata_json=relationship.metadata_json,
        )
        self.session.merge(model)

    def get(self, relationship_id: UUID) -> Relationship | None:
        model = self.session.get(RelationshipModel, relationship_id)
        if not model:
            return None
        return self._to_entity(model)

    def delete(self, relationship_id: UUID) -> None:
        model = self.session.get(RelationshipModel, relationship_id)
        if model:
            self.session.delete(model)

    def list_outgoing(self, entity_id: UUID) -> list[Relationship]:
        models = self.session.exec(select(RelationshipModel).where(RelationshipModel.from_id == entity_id)).all()
        return [self._to_entity(model) for model in models]

    def list_incoming(self, entity_id: UUID) -> list[Relationship]:
        models = self.session.exec(select(RelationshipModel).where(RelationshipModel.to_id == entity_id)).all()
        return [self._to_entity(model) for model in models]

    def list_by_type(self, relationship_type: RelationshipType) -> list[Relationship]:
        models = self.session.exec(
            select(RelationshipModel).where(RelationshipModel.relationship_type == relationship_type)
        ).all()
        return [self._to_entity(model) for model in models]

    def list(self, limit: int = 50, offset: int = 0) -> list[Relationship]:
        models = self.session.exec(
            select(RelationshipModel).order_by(RelationshipModel.created_at.desc()).offset(offset).limit(limit)
        ).all()
        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: RelationshipModel) -> Relationship:
        return Relationship(
            id=model.id,
            from_id=model.from_id,
            from_type=model.from_type,
            to_id=model.to_id,
            to_type=model.to_type,
            relationship_type=model.relationship_type,
            confidence=model.confidence,
            created_by=model.created_by,
            created_at=model.created_at,
            metadata_json=model.metadata_json,
        )
