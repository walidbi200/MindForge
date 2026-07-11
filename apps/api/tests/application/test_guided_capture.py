from unittest.mock import Mock

from ascend.application.ai.protocols import AIConceptSuggestion, AIResponse
from ascend.application.workspace.start_guided_capture import StartGuidedCaptureUseCase
from ascend.domain.captures.entity import Capture
from ascend.infrastructure.events.bus import EventBus
from ascend.infrastructure.uow import SqlAlchemyUnitOfWork


def test_start_guided_capture(db_session):
    bus = EventBus()
    uow = SqlAlchemyUnitOfWork(db_session, bus)

    mock_ai_service = Mock()
    mock_ai_service.generate.return_value = AIResponse(
        summary="API Summary",
        concepts=[AIConceptSuggestion(name="Concept 1", description="Desc 1", confidence=0.9)],
        questions=["What is this?"],
        collections=["Test Collection"],
        review_suggestion="1_WEEK",
    )

    use_case = StartGuidedCaptureUseCase(uow, mock_ai_service)
    capture, response = use_case.execute("Testing guided capture")

    assert isinstance(capture, Capture)
    assert capture.content == "Testing guided capture"
    assert response.summary == "API Summary"
    assert len(response.concepts) == 1

    # Verify that the capture was saved
    with uow:
        saved = uow.captures.get(capture.id)
        assert saved is not None
        assert saved.content == "Testing guided capture"
