from datetime import datetime, timezone
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.collections.entity import Membership
from ascend.domain.events.collection_events import EntityAddedToCollection
from ascend.domain.relationships.entity import EntityType


class AddEntityToCollectionUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(
        self,
        membership_id: UUID,
        collection_id: UUID,
        entity_id: UUID,
        entity_type: EntityType,
    ) -> Membership:
        with self.uow:
            # 1. Validate collection exists
            collection = self.uow.collections.get(collection_id)
            if not collection:
                raise ValueError(f"Collection {collection_id} does not exist.")

            # 2. Validate entity exists (per-type explicit validation)
            if entity_type == EntityType.CAPTURE:
                if not self.uow.captures.get(entity_id):
                    raise ValueError(f"Capture {entity_id} does not exist.")
            elif entity_type == EntityType.CONCEPT:
                if not self.uow.concepts.get(entity_id):
                    raise ValueError(f"Concept {entity_id} does not exist.")
            elif entity_type == EntityType.SOURCE:
                if not self.uow.sources.get(entity_id):
                    raise ValueError(f"Source {entity_id} does not exist.")
            else:
                raise ValueError(f"Unsupported entity type: {entity_type}")

            # 3. Validate duplicate membership
            existing = self.uow.memberships.find(collection_id, entity_id)
            if existing:
                raise ValueError("Entity is already a member of this collection.")

            now = datetime.now(timezone.utc)
            membership = Membership(
                id=membership_id,
                collection_id=collection_id,
                entity_id=entity_id,
                entity_type=entity_type,
                created_at=now,
            )

            self.uow.memberships.save(membership)
            self.uow.emit(
                EntityAddedToCollection(
                    aggregate_id=collection_id,
                    entity_id=str(entity_id),
                    entity_type=entity_type,
                )
            )
            self.uow.commit()

        return membership
