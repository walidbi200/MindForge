from datetime import datetime, timezone
from uuid import uuid4

from ascend.application.concepts.update_concept import UpdateConceptUseCase
from ascend.application.graph.merge_concepts import MergeConceptsUseCase
from ascend.application.relationships.create_relationship import CreateRelationshipUseCase
from ascend.application.collections.create_collection import CreateCollectionUseCase
from ascend.application.collections.add_entity_to_collection import AddEntityToCollectionUseCase
from ascend.domain.concepts.entity import Concept
from ascend.domain.relationships.entity import CreatorType, EntityType, RelationshipType
from ascend.infrastructure.events.bus import EventBus
from ascend.infrastructure.uow import SqlAlchemyUnitOfWork


def test_update_concept(db_session):
    bus = EventBus()
    uow = SqlAlchemyUnitOfWork(db_session, bus)

    concept_id = uuid4()
    with uow:
        uow.concepts.save(Concept(id=concept_id, title="Old Title", summary="Old Summary", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)))
        uow.commit()

    use_case = UpdateConceptUseCase(uow)
    updated_concept = use_case.execute(concept_id, title="New Title")

    assert updated_concept.title == "New Title"
    assert updated_concept.summary == "Old Summary"

    with uow:
        db_concept = uow.concepts.get(concept_id)
        assert db_concept.title == "New Title"


def test_merge_concepts(db_session):
    bus = EventBus()
    uow = SqlAlchemyUnitOfWork(db_session, bus)

    source_id = uuid4()
    target_id = uuid4()
    other_id = uuid4()
    
    with uow:
        uow.concepts.save(Concept(id=source_id, title="Source Concept", summary="Source", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)))
        uow.concepts.save(Concept(id=target_id, title="Target Concept", summary="Target", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)))
        uow.concepts.save(Concept(id=other_id, title="Other Concept", summary="Other", created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)))
        uow.commit()

    # Create a relationship where source is the from_id
    CreateRelationshipUseCase(uow).execute(
        uuid4(), source_id, EntityType.CONCEPT, other_id, EntityType.CONCEPT, RelationshipType.RELATED_TO, 1.0, CreatorType.SYSTEM
    )
    
    # Create a relationship where source is the to_id
    CreateRelationshipUseCase(uow).execute(
        uuid4(), other_id, EntityType.CONCEPT, source_id, EntityType.CONCEPT, RelationshipType.RELATED_TO, 1.0, CreatorType.SYSTEM
    )
    
    # Put source in a collection
    col_id = uuid4()
    CreateCollectionUseCase(uow).execute(col_id, "Test Col", "Desc", "color", "icon")
    AddEntityToCollectionUseCase(uow).execute(uuid4(), col_id, source_id, EntityType.CONCEPT)

    merge_use_case = MergeConceptsUseCase(uow)
    merge_use_case.execute(source_id, target_id)

    with uow:
        assert uow.concepts.get(source_id) is None
        assert uow.concepts.get(target_id) is not None
        
        outgoing = uow.relationships.list_outgoing(target_id)
        assert len(outgoing) == 1
        assert outgoing[0].to_id == other_id
        
        incoming = uow.relationships.list_incoming(target_id)
        assert len(incoming) == 1
        assert incoming[0].from_id == other_id
        
        mems = uow.memberships.list_by_entity(target_id)
        assert len(mems) == 1
        assert mems[0].collection_id == col_id
