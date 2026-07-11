from uuid import UUID

from fastapi import APIRouter, Depends

from ascend.api.dependencies import get_uow
from ascend.api.v1.endpoints.ai.schemas import AnalyzeCaptureResponse, ApplyAnalysisRequest
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
        relationships=[r.model_dump(by_alias=True) for r in response.relationships],
        questions=response.questions,
        collections=response.collections,
        review_suggestion=response.review_suggestion,
    )


@router.post("/apply-analysis/{capture_id}", status_code=200)
def apply_analysis(
    capture_id: UUID,
    request: ApplyAnalysisRequest,
    uow: UnitOfWork = Depends(get_uow),
):
    """
    Applies the accepted AI suggestions for a capture to the Knowledge Graph.
    """
    from ascend.application.ai.apply_analysis import ApplyAIAnalysisUseCase
    from ascend.application.ai.protocols import AIConceptSuggestion, AIRelationshipSuggestion

    use_case = ApplyAIAnalysisUseCase(uow)

    # Map Pydantic request models to protocol suggestions
    concepts = [
        AIConceptSuggestion(name=c.name, description=c.description, confidence=c.confidence) for c in request.concepts
    ]
    relationships = [
        AIRelationshipSuggestion(
            **{"from": r.from_entity, "to": r.to_entity, "type": r.relationship_type}, confidence=r.confidence
        )
        for r in request.relationships
    ]

    use_case.execute(
        capture_id=capture_id,
        concepts=concepts,
        relationships=relationships,
        collections=request.collections,
        review_suggestion=request.review_suggestion,
    )

    return {"status": "success"}
