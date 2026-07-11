from datetime import datetime, timezone
from uuid import uuid4

from ascend.application.workspace.apply_proposal import ApplyProposalUseCase, ConceptProposal, RelationshipProposal
from ascend.domain.captures.entity import Capture
from ascend.infrastructure.events.bus import EventBus
from ascend.infrastructure.uow import SqlAlchemyUnitOfWork


def test_apply_proposal(db_session):
    bus = EventBus()
    uow = SqlAlchemyUnitOfWork(db_session, bus)

    with uow:
        capture = Capture(id=uuid4(), content="Test content", created_at=datetime.now(timezone.utc))
        uow.captures.save(capture)
        uow.commit()

    use_case = ApplyProposalUseCase(uow)

    concepts = [
        ConceptProposal(name="App Concept 1", description="Desc 1", confidence=0.9),
        ConceptProposal(name="App Concept 2", description="Desc 2", confidence=0.8),
    ]
    relationships = [
        RelationshipProposal(
            from_entity="App Concept 1",
            to_entity="App Concept 2",
            relationship_type="RELATED_TO",
            confidence=0.95,
        )
    ]
    collections = ["App Collection"]
    review_suggestion = "1_WEEK"

    use_case.execute(
        capture_id=capture.id,
        concepts=concepts,
        relationships=relationships,
        collections=collections,
        review_suggestion=review_suggestion,
    )

    with uow:
        updated_capture = uow.captures.get(capture.id)
        assert updated_capture.status.value == "PROCESSED"

        saved_concepts = [c for c in uow.concepts.list() if c.title in ["App Concept 1", "App Concept 2"]]
        assert len(saved_concepts) == 2

        saved_cols = [c for c in uow.collections.list() if c.name == "App Collection"]
        assert len(saved_cols) == 1

        saved_reviews = uow.reviews.list_by_entity(capture.id)
        assert len(saved_reviews) == 1
