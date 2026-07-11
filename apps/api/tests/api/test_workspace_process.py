from unittest.mock import patch

from ascend.application.ai.protocols import AIConceptSuggestion, AIResponse


def test_process_capture_api(test_client, db_session):
    with patch("ascend.api.v1.endpoints.workspace.router.OpenRouterAIService") as MockAIService:
        mock_instance = MockAIService.return_value
        mock_instance.generate.return_value = AIResponse(
            summary="API Summary",
            concepts=[AIConceptSuggestion(name="Concept 1", description="Desc 1", confidence=0.9)],
            questions=["What is this?"],
            collections=["Test Collection"],
            review_suggestion="1_WEEK",
        )

        response = test_client.post("/api/v1/workspace/process-capture", json={"content": "Test capture"})

    assert response.status_code == 200
    data = response.json()
    assert "capture_id" in data
    assert data["proposal"]["summary"] == "API Summary"
    assert len(data["proposal"]["concepts"]) == 1
    assert data["proposal"]["concepts"][0]["name"] == "Concept 1"
    assert data["proposal"]["collections"] == ["Test Collection"]
    assert data["proposal"]["review_suggestion"] == "1_WEEK"


def test_apply_proposal_api(test_client, db_session):
    # Process a capture first to have a valid capture
    from datetime import datetime, timezone
    from uuid import uuid4

    from ascend.domain.captures.entity import Capture
    from ascend.infrastructure.events.bus import EventBus
    from ascend.infrastructure.uow import SqlAlchemyUnitOfWork

    bus = EventBus()
    uow = SqlAlchemyUnitOfWork(db_session, bus)
    with uow:
        capture = Capture(id=uuid4(), content="Test content", created_at=datetime.now(timezone.utc))
        uow.captures.save(capture)
        uow.commit()

    payload = {
        "capture_id": str(capture.id),
        "proposal": {
            "summary": "Some summary",
            "concepts": [
                {"name": "API Concept 1", "description": "Desc 1", "confidence": 0.9},
                {"name": "API Concept 2", "description": "Desc 2", "confidence": 0.8},
            ],
            "relationships": [
                {
                    "from_entity": "API Concept 1",
                    "to_entity": "API Concept 2",
                    "relationship_type": "RELATED_TO",
                    "confidence": 0.95,
                }
            ],
            "collections": ["API Collection"],
            "review_suggestion": "1_WEEK",
        }
    }

    response = test_client.post("/api/v1/workspace/apply-proposal", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify state changes
    with uow:
        updated_capture = uow.captures.get(capture.id)
        assert updated_capture.status.value == "PROCESSED"

        # Check concepts
        concepts = [c for c in uow.concepts.list() if c.title in ["API Concept 1", "API Concept 2"]]
        assert len(concepts) == 2

        # Check collections
        cols = [c for c in uow.collections.list() if c.name == "API Collection"]
        assert len(cols) == 1

        # Check reviews
        reviews = uow.reviews.list_by_entity(capture.id)
        assert len(reviews) == 1
