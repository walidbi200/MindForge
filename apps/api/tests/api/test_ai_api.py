from datetime import datetime, timezone
from unittest.mock import patch
from uuid import uuid4

from ascend.application.ai.protocols import AIConceptSuggestion, AIResponse


def test_analyze_capture_api(test_client, db_session):
    # Setup test capture
    from ascend.domain.captures.entity import Capture
    from ascend.infrastructure.events.bus import EventBus
    from ascend.infrastructure.uow import SqlAlchemyUnitOfWork

    bus = EventBus()
    uow = SqlAlchemyUnitOfWork(db_session, bus)
    with uow:
        capture = Capture(id=uuid4(), content="Test content", created_at=datetime.now(timezone.utc))
        uow.captures.save(capture)
        uow.commit()

    # Mock the OpenRouterAIService
    with patch("ascend.api.v1.endpoints.ai.router.OpenRouterAIService") as MockAIService:
        mock_instance = MockAIService.return_value
        mock_instance.generate.return_value = AIResponse(
            summary="API Summary",
            concepts=[AIConceptSuggestion(name="Concept 1", description="Desc 1", confidence=0.9)],
            questions=["What is this?"],
        )

        response = test_client.post(f"/api/v1/ai/analyze-capture/{capture.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "API Summary"
    assert len(data["concepts"]) == 1
    assert data["concepts"][0]["name"] == "Concept 1"
    assert data["questions"] == ["What is this?"]


def test_analyze_capture_not_found(test_client):
    with patch("ascend.api.v1.endpoints.ai.router.OpenRouterAIService"):
        response = test_client.post(f"/api/v1/ai/analyze-capture/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_apply_analysis_api(test_client, db_session):
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
        "concepts": [
            {"name": "Concept 1", "description": "Desc 1", "confidence": 0.9},
            {"name": "Concept 2", "description": "Desc 2", "confidence": 0.8},
        ],
        "relationships": [{"from": "Concept 1", "to": "Concept 2", "type": "RELATED_TO", "confidence": 0.95}],
        "collections": ["Inbox Collection"],
        "review_suggestion": "1_WEEK",
    }

    response = test_client.post(f"/api/v1/ai/apply-analysis/{capture.id}", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify state changes
    with uow:
        updated_capture = uow.captures.get(capture.id)
        assert updated_capture.status.value == "PROCESSED"

        # Check concepts
        concepts = uow.concepts.list()
        assert len(concepts) == 2

        # Check collections
        cols = uow.collections.list()
        assert len(cols) == 1
        assert cols[0].name == "Inbox Collection"

        # Check reviews
        reviews = uow.reviews.list_by_entity(capture.id)
        assert len(reviews) == 1
