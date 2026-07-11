from dataclasses import dataclass
from uuid import UUID

from ascend.application.uow import UnitOfWork


@dataclass
class RecommendationResult:
    id: UUID
    type: str
    title: str
    reason: str
    score: float


class GetKnowledgeRecommendationsUseCase:
    """
    Deterministic recommendations based on graph proximity, shared collections, and timeline history.
    No ML models or embeddings are used here.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, entity_id: UUID, limit: int = 5) -> list[RecommendationResult]:
        recommendations: dict[UUID, RecommendationResult] = {}

        def add_rec(rec_id: UUID, rec_type: str, title: str, reason: str, score: float):
            if rec_id == entity_id:
                return
            if rec_id in recommendations:
                recommendations[rec_id].score += score
            else:
                recommendations[rec_id] = RecommendationResult(
                    id=rec_id, type=rec_type, title=title, reason=reason, score=score
                )

        with self.uow:
            # 1. Graph Relationships (1-hop)
            outgoing = self.uow.relationships.list_outgoing(entity_id)
            incoming = self.uow.relationships.list_incoming(entity_id)
            for rel in outgoing:
                add_rec(rel.to_id, rel.to_type.value, "Related Entity", "Direct connection", 2.0)
            for rel in incoming:
                add_rec(rel.from_id, rel.from_type.value, "Related Entity", "Direct connection", 2.0)

            # 2. Shared Collections
            memberships = self.uow.memberships.list_by_entity(entity_id)
            for m in memberships:
                col_members = self.uow.memberships.list_by_collection(m.collection_id)
                for cm in col_members:
                    if cm.entity_id != entity_id:
                        add_rec(cm.entity_id, cm.entity_type.value, "Related Entity", "Shared collection", 1.5)

            # 3. Timeline Activity (Entities interacted with recently around the same time as this entity)
            # Find the most recent interaction with this entity
            events = self.uow.timeline.list(limit=200)
            entity_event_idx = None
            for i, event in enumerate(events):
                if event.aggregate_id == entity_id:
                    entity_event_idx = i
                    break

            if entity_event_idx is not None:
                # Look at events closely following or preceding this interaction
                start_idx = max(0, entity_event_idx - 5)
                end_idx = min(len(events), entity_event_idx + 6)
                for i in range(start_idx, end_idx):
                    if i != entity_event_idx:
                        event = events[i]
                        add_rec(event.aggregate_id, event.aggregate_type, "Related Entity", "Recent activity", 1.0)

            # Look up actual titles for the top recommended items
            sorted_recs = sorted(recommendations.values(), key=lambda r: r.score, reverse=True)[:limit]

            # Batch fetch to resolve titles
            concept_ids = [r.id for r in sorted_recs if r.type == "Concept"]
            capture_ids = [r.id for r in sorted_recs if r.type == "Capture"]
            source_ids = [r.id for r in sorted_recs if r.type == "Source"]
            collection_ids = [r.id for r in sorted_recs if r.type == "Collection"]

            concepts = (
                {c.id: c.title for c in self.uow.concepts.list_by_ids(concept_ids)}
                if concept_ids else {}
            )
            captures = (
                {c.id: c.content[:30] + "..." for c in self.uow.captures.list_by_ids(capture_ids)}
                if capture_ids else {}
            )
            sources = (
                {s.id: s.title for s in self.uow.sources.list_by_ids(source_ids)}
                if source_ids else {}
            )
            collections = (
                {c.id: c.name for c in self.uow.collections.list_by_ids(collection_ids)}
                if collection_ids else {}
            )

            final_recs = []
            for r in sorted_recs:
                title = None
                if r.type == "Concept":
                    title = concepts.get(r.id)
                elif r.type == "Capture":
                    title = captures.get(r.id)
                elif r.type == "Source":
                    title = sources.get(r.id)
                elif r.type == "Collection":
                    title = collections.get(r.id)

                if title:
                    r.title = title
                    final_recs.append(r)

            return final_recs
