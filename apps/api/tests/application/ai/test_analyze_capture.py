from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from ascend.application.ai.analyze_capture import AnalyzeCaptureUseCase
from ascend.application.ai.protocols import AIConceptSuggestion, AIRequest, AIResponse
from ascend.domain.events.ai_events import AIAnalysisCompleted, AIAnalysisFailed, AIAnalysisRequested
from ascend.domain.exceptions import EntityNotFoundError


def test_analyze_capture_success():
    # Setup
    capture_id = uuid4()
    mock_uow = MagicMock()
    mock_capture = MagicMock(id=capture_id, content="Some note")
    mock_uow.captures.get.return_value = mock_capture

    mock_ai_service = MagicMock()
    mock_ai_service.generate.return_value = AIResponse(
        summary="A summary",
        concepts=[AIConceptSuggestion(name="Concept 1", description="Desc 1", confidence=0.9)],
        metadata={"prompt_tokens": 10, "completion_tokens": 20, "latency_ms": 150},
    )

    use_case = AnalyzeCaptureUseCase(mock_uow, mock_ai_service)

    # Execute
    response = use_case.execute(capture_id)

    # Assertions
    assert response.summary == "A summary"
    assert len(response.concepts) == 1

    # Verify AI Service was called
    mock_ai_service.generate.assert_called_once()
    request = mock_ai_service.generate.call_args[0][0]
    assert isinstance(request, AIRequest)
    assert "Some note" in request.user_prompt

    # Verify Events
    assert mock_uow.emit.call_count == 2
    events = [call.args[0] for call in mock_uow.emit.call_args_list]
    assert isinstance(events[0], AIAnalysisRequested)
    assert isinstance(events[1], AIAnalysisCompleted)

    # Verify UoW commit was called
    mock_uow.commit.assert_called_once()


def test_analyze_capture_not_found():
    mock_uow = MagicMock()
    mock_uow.captures.get.return_value = None
    mock_ai_service = MagicMock()

    use_case = AnalyzeCaptureUseCase(mock_uow, mock_ai_service)

    with pytest.raises(EntityNotFoundError):
        use_case.execute(uuid4())

    mock_ai_service.generate.assert_not_called()


def test_analyze_capture_ai_failure():
    capture_id = uuid4()
    mock_uow = MagicMock()
    mock_capture = MagicMock(id=capture_id, content="Some note")
    mock_uow.captures.get.return_value = mock_capture

    mock_ai_service = MagicMock()
    mock_ai_service.generate.side_effect = Exception("OpenRouter is down")

    use_case = AnalyzeCaptureUseCase(mock_uow, mock_ai_service)

    with pytest.raises(Exception):
        use_case.execute(capture_id)

    # Verify Events
    assert mock_uow.emit.call_count == 2
    events = [call.args[0] for call in mock_uow.emit.call_args_list]
    assert isinstance(events[0], AIAnalysisRequested)
    assert isinstance(events[1], AIAnalysisFailed)
    assert events[1].error_message == "OpenRouter is down"

    mock_uow.commit.assert_called_once()
