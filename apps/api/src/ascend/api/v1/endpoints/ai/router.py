from uuid import UUID

from fastapi import APIRouter, Depends

from ascend.api.dependencies import get_uow
from ascend.api.v1.endpoints.ai.schemas import AnalyzeCaptureResponse
from ascend.application.ai.analyze_capture import AnalyzeCaptureUseCase
from ascend.application.uow import UnitOfWork
from ascend.infrastructure.ai.openrouter import OpenRouterAIService

router = APIRouter()


@router.post("/analyze-capture/{capture_id}", response_model=AnalyzeCaptureResponse)
def analyze_capture(
    capture_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
) -> AnalyzeCaptureResponse:
    """
    Analyze a capture using the configured AI service.
    Returns structured suggestions (concepts, relationships, summary, questions)
    without persisting them to the database.
    """
    ai_service = OpenRouterAIService()
    use_case = AnalyzeCaptureUseCase(uow, ai_service)

    response = use_case.execute(capture_id)

    return AnalyzeCaptureResponse(
        summary=response.summary,
        concepts=[c.model_dump() for c in response.concepts],
        relationships=[r.model_dump() for r in response.relationships],
        questions=response.questions,
    )
