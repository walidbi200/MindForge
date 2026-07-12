from uuid import UUID

from ascend.application.uow import UnitOfWork
from ascend.domain.exceptions import NotFoundError, ConflictError
from ascend.domain.events.concept_events import ConceptsMerged


class MergeConceptsUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def execute(self, source_id: UUID, target_id: UUID) -> None:
        if source_id == target_id:
            raise ConflictError("Cannot merge a concept into itself")

        with self.uow:
            source = self.uow.concepts.get(source_id)
            target = self.uow.concepts.get(target_id)

            if not source:
                raise NotFoundError(f"Source Concept {source_id} not found")
            if not target:
                raise NotFoundError(f"Target Concept {target_id} not found")

            # 1. Move relationships
            outgoing_source = self.uow.relationships.list_outgoing(source_id)
            outgoing_target = self.uow.relationships.list_outgoing(target_id)
            target_outgoing_pairs = {(r.to_id, r.relationship_type) for r in outgoing_target}

            for rel in outgoing_source:
                if (rel.to_id, rel.relationship_type) in target_outgoing_pairs or rel.to_id == target_id:
                    self.uow.relationships.delete(rel.id)
                else:
                    rel.from_id = target_id
                    self.uow.relationships.save(rel)

            incoming_source = self.uow.relationships.list_incoming(source_id)
            incoming_target = self.uow.relationships.list_incoming(target_id)
            target_incoming_pairs = {(r.from_id, r.relationship_type) for r in incoming_target}

            for rel in incoming_source:
                if (rel.from_id, rel.relationship_type) in target_incoming_pairs or rel.from_id == target_id:
                    self.uow.relationships.delete(rel.id)
                else:
                    rel.to_id = target_id
                    self.uow.relationships.save(rel)

            # 2. Move collection memberships
            memberships_source = self.uow.memberships.list_by_entity(source_id)
            memberships_target = self.uow.memberships.list_by_entity(target_id)
            target_col_ids = {m.collection_id for m in memberships_target}

            for mem in memberships_source:
                if mem.collection_id in target_col_ids:
                    self.uow.memberships.delete(mem.id)
                else:
                    mem.entity_id = target_id
                    self.uow.memberships.save(mem)

            # 3. Move reviews
            reviews_source = self.uow.reviews.list_by_entity(source_id)
            for rev in reviews_source:
                rev.entity_id = target_id
                self.uow.reviews.save(rev)

            # 4. Delete source concept
            self.uow.concepts.delete(source_id)

            # 5. Emit event
            self.uow.emit(ConceptsMerged(aggregate_id=target_id, source_id=str(source_id), target_id=str(target_id)))

            self.uow.commit()
