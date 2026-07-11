from dataclasses import dataclass
from typing import Any
from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.captures.entity import Capture
from ascend.domain.collections.entity import Collection
from ascend.domain.concepts.entity import Concept
from ascend.domain.relationships.entity import EntityType, Relationship
from ascend.domain.sources.entity import Source


@dataclass
class KnowledgeNeighborhoodResult:
    center: dict[str, Any]
    concepts: list[Concept]
    captures: list[Capture]
    sources: list[Source]
    collections: list[Collection]
    relationships: list[Relationship]


class GetKnowledgeNeighborhoodUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, entity_id: UUID) -> KnowledgeNeighborhoodResult | None:
        with self.uow:
            # 1. Fetch Center Entity
            center_data = self._fetch_center(entity_id)
            if not center_data:
                return None

            # 2. Fetch Relationships
            outgoing = self.uow.relationships.list_outgoing(entity_id)
            incoming = self.uow.relationships.list_incoming(entity_id)
            relationships = outgoing + incoming

            # Dedup relationships
            seen_rels = set()
            unique_relationships = []
            for r in relationships:
                if r.id not in seen_rels:
                    seen_rels.add(r.id)
                    unique_relationships.append(r)

            # 3. Fetch Connected Entities
            concept_ids = set()
            capture_ids = set()
            source_ids = set()

            for rel in unique_relationships:
                target_id = rel.to_id if rel.from_id == entity_id else rel.from_id
                target_type = rel.to_type if rel.from_id == entity_id else rel.from_type

                if target_type == EntityType.CONCEPT:
                    concept_ids.add(target_id)
                elif target_type == EntityType.CAPTURE:
                    capture_ids.add(target_id)
                elif target_type == EntityType.SOURCE:
                    source_ids.add(target_id)

            concepts = self.uow.concepts.list_by_ids(list(concept_ids)) if concept_ids else []
            captures = self.uow.captures.list_by_ids(list(capture_ids)) if capture_ids else []
            sources = self.uow.sources.list_by_ids(list(source_ids)) if source_ids else []

            # 4. Fetch Memberships & Collections
            memberships = self.uow.memberships.list_by_entity(entity_id)
            collection_ids = [m.collection_id for m in memberships]
            collections = self.uow.collections.list_by_ids(list(collection_ids)) if collection_ids else []

            return KnowledgeNeighborhoodResult(
                center=center_data,
                concepts=concepts,
                captures=captures,
                sources=sources,
                collections=collections,
                relationships=unique_relationships,
            )

    def _fetch_center(self, entity_id: UUID) -> dict[str, Any] | None:
        # Try concept
        concept = self.uow.concepts.get(entity_id)
        if concept:
            return {"type": "Concept", "data": concept}

        # Try source
        source = self.uow.sources.get(entity_id)
        if source:
            return {"type": "Source", "data": source}

        # Try capture
        capture = self.uow.captures.get(entity_id)
        if capture:
            return {"type": "Capture", "data": capture}

        return None
