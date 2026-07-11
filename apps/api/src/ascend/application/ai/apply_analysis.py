from datetime import datetime, timezone
from uuid import UUID, uuid4

from ascend.application.ai.protocols import AIConceptSuggestion, AIRelationshipSuggestion
from ascend.domain.captures.entity import CaptureStatus
from ascend.domain.collections.entity import Collection, Membership
from ascend.domain.concepts.entity import Concept
from ascend.domain.events.capture_events import CaptureUpdated
from ascend.domain.events.collection_events import CollectionCreated, EntityAddedToCollection
from ascend.domain.events.concept_events import ConceptCreated
from ascend.domain.events.relationship_events import RelationshipCreated
from ascend.domain.events.review_events import ReviewCreated
from ascend.domain.exceptions import NotFoundError
from ascend.domain.relationships.entity import CreatorType, EntityType, Relationship
from ascend.domain.reviews.entity import Review, ReviewStatus
from ascend.infrastructure.uow import UnitOfWork


class ApplyAIAnalysisUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(
        self,
        capture_id: UUID,
        concepts: list[AIConceptSuggestion],
        relationships: list[AIRelationshipSuggestion],
        collections: list[str],
        review_suggestion: str | None = None,
    ) -> None:
        with self.uow:
            capture = self.uow.captures.get(capture_id)
            if not capture:
                raise NotFoundError(f"Capture with id {capture_id} not found.")

            # Map generated concept names to their created UUIDs for relationships
            concept_name_to_id: dict[str, UUID] = {}

            # Create Concepts
            for concept_data in concepts:
                concept_id = uuid4()
                concept = Concept(
                    id=concept_id,
                    title=concept_data.name,
                    summary=concept_data.description,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                self.uow.concepts.save(concept)
                self.uow.emit(ConceptCreated(aggregate_id=concept.id, title=concept.title, summary=concept.summary))
                concept_name_to_id[concept_data.name] = concept_id

                # Create MENTIONS relationship from Capture to Concept
                rel_id = uuid4()
                from ascend.domain.relationships.entity import RelationshipType

                rel = Relationship(
                    id=rel_id,
                    from_id=capture_id,
                    from_type=EntityType.CAPTURE,
                    to_id=concept_id,
                    to_type=EntityType.CONCEPT,
                    relationship_type=RelationshipType.GENERATED_FROM,
                    confidence=1.0,
                    created_by=CreatorType.AI,
                    created_at=datetime.now(timezone.utc),
                    metadata_json="{}",
                )
                self.uow.relationships.save(rel)
                self.uow.emit(
                    RelationshipCreated(
                        aggregate_id=rel.id,
                        from_id=str(rel.from_id),
                        from_type=rel.from_type,
                        to_id=str(rel.to_id),
                        to_type=rel.to_type,
                        relationship_type=rel.relationship_type,
                    )
                )

            # Create Relationships between Concepts
            for rel_data in relationships:
                from_id = concept_name_to_id.get(rel_data.from_entity)
                to_id = concept_name_to_id.get(rel_data.to_entity)
                if from_id and to_id:
                    rel_id = uuid4()
                    rel_type_str = rel_data.relationship_type
                    try:
                        rel_type = RelationshipType(rel_type_str)
                    except ValueError:
                        rel_type = RelationshipType.RELATED_TO

                    rel = Relationship(
                        id=rel_id,
                        from_id=from_id,
                        from_type=EntityType.CONCEPT,
                        to_id=to_id,
                        to_type=EntityType.CONCEPT,
                        relationship_type=rel_type,
                        confidence=rel_data.confidence,
                        created_by=CreatorType.AI,
                        created_at=datetime.now(timezone.utc),
                        metadata_json="{}",
                    )
                    self.uow.relationships.save(rel)
                    self.uow.emit(
                        RelationshipCreated(
                            aggregate_id=rel.id,
                            from_id=str(rel.from_id),
                            from_type=rel.from_type,
                            to_id=str(rel.to_id),
                            to_type=rel.to_type,
                            relationship_type=rel.relationship_type,
                        )
                    )

            # Assign to Collections (creating them if they don't exist)
            for collection_name in collections:
                existing_cols = self.uow.collections.list(limit=1000)
                col = next((c for c in existing_cols if c.name == collection_name), None)
                if not col:
                    col = Collection(
                        id=uuid4(),
                        name=collection_name,
                        description="Auto-generated tag",
                        color="#4F46E5",
                        icon="tag",
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc),
                    )
                    self.uow.collections.save(col)
                    self.uow.emit(CollectionCreated(aggregate_id=col.id, name=col.name))

                # Assign Capture to Collection
                membership_id = uuid4()
                membership = Membership(
                    id=membership_id,
                    collection_id=col.id,
                    entity_id=capture_id,
                    entity_type=EntityType.CAPTURE,
                    created_at=datetime.now(timezone.utc),
                )
                existing_member = self.uow.memberships.find(col.id, capture_id)
                if not existing_member:
                    self.uow.memberships.save(membership)
                    self.uow.emit(
                        EntityAddedToCollection(
                            aggregate_id=col.id, entity_id=str(capture_id), entity_type=EntityType.CAPTURE
                        )
                    )

            # Review Suggestion
            if review_suggestion and review_suggestion != "NEVER":
                from datetime import timedelta

                delta = timedelta(days=1)
                if review_suggestion == "1_WEEK":
                    delta = timedelta(days=7)
                elif review_suggestion == "1_MONTH":
                    delta = timedelta(days=30)

                due_date = datetime.now(timezone.utc) + delta
                review_id = uuid4()
                review = Review(
                    id=review_id,
                    entity_id=capture_id,
                    entity_type=EntityType.CAPTURE,
                    status=ReviewStatus.PENDING,
                    due_at=due_date,
                    completed_at=None,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                self.uow.reviews.save(review)
                self.uow.emit(
                    ReviewCreated(aggregate_id=review.id, entity_id=str(capture_id), entity_type=EntityType.CAPTURE)
                )

            # Mark capture as processed
            capture.status = CaptureStatus.PROCESSED
            self.uow.captures.save(capture)
            self.uow.emit(CaptureUpdated(aggregate_id=capture.id, content=capture.content))

            self.uow.commit()
