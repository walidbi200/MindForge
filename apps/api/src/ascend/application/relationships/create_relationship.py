import json
from datetime import datetime, timezone
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.events.relationship_events import RelationshipCreated
from ascend.domain.exceptions import ConflictError, EntityNotFoundError, ValidationError
from ascend.domain.relationships.entity import CreatorType, EntityType, Relationship, RelationshipType


class CreateRelationshipUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(
        self,
        relationship_id: UUID,
        from_id: UUID,
        from_type: EntityType,
        to_id: UUID,
        to_type: EntityType,
        relationship_type: RelationshipType,
        confidence: float,
        created_by: CreatorType,
        metadata_dict: dict | None = None,
    ) -> Relationship:
        if from_id == to_id:
            raise ValidationError("Self-links are not allowed.")

        if not (0.0 <= confidence <= 1.0):
            raise ValidationError("Confidence must be between 0.0 and 1.0.")

        metadata_json = json.dumps(metadata_dict) if metadata_dict is not None else "{}"

        with self.uow:
            # Validate `from_id` exists
            if from_type == EntityType.CAPTURE:
                if not self.uow.captures.get(from_id):
                    raise EntityNotFoundError(f"Capture {from_id} does not exist.")
            elif from_type == EntityType.CONCEPT:
                if not self.uow.concepts.get(from_id):
                    raise EntityNotFoundError(f"Concept {from_id} does not exist.")
            elif from_type == EntityType.SOURCE:
                if not self.uow.sources.get(from_id):
                    raise EntityNotFoundError(f"Source {from_id} does not exist.")

            # Validate `to_id` exists
            if to_type == EntityType.CAPTURE:
                if not self.uow.captures.get(to_id):
                    raise EntityNotFoundError(f"Capture {to_id} does not exist.")
            elif to_type == EntityType.CONCEPT:
                if not self.uow.concepts.get(to_id):
                    raise EntityNotFoundError(f"Concept {to_id} does not exist.")
            elif to_type == EntityType.SOURCE:
                if not self.uow.sources.get(to_id):
                    raise EntityNotFoundError(f"Source {to_id} does not exist.")

            # Validate uniqueness
            existing = self.uow.relationships.list_outgoing(from_id)
            for rel in existing:
                if rel.to_id == to_id and rel.relationship_type == relationship_type:
                    raise ConflictError("Duplicate relationship.")

            now = datetime.now(timezone.utc)
            relationship = Relationship(
                id=relationship_id,
                from_id=from_id,
                from_type=from_type,
                to_id=to_id,
                to_type=to_type,
                relationship_type=relationship_type,
                confidence=confidence,
                created_by=created_by,
                created_at=now,
                metadata_json=metadata_json,
            )

            self.uow.relationships.save(relationship)

            event = RelationshipCreated(
                aggregate_id=relationship.id,
                from_id=str(relationship.from_id),
                from_type=relationship.from_type,
                to_id=str(relationship.to_id),
                to_type=relationship.to_type,
                relationship_type=relationship.relationship_type,
            )
            self.uow.emit(event)
            self.uow.commit()

        return relationship
