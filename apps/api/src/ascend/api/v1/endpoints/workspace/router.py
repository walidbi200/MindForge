import json

from fastapi import APIRouter, Depends

from ascend.api.dependencies import get_uow
from ascend.api.v1.endpoints.captures.mappers import to_response as capture_to_response
from ascend.api.v1.endpoints.collections.router import to_collection_response
from ascend.api.v1.endpoints.concepts.router import to_response as concept_to_response
from ascend.api.v1.endpoints.sources.router import to_response as source_to_response
from ascend.api.v1.endpoints.timeline.schemas import TimelineEventResponse
from ascend.api.v1.endpoints.workspace.schemas import (
    AIProposalResponse,
    ApplyProposalRequest,
    ConceptSuggestionResponse,
    ContinueLearningResponse,
    DailyStatsResponse,
    PendingProposalResponse,
    ProcessCaptureRequest,
    ProcessCaptureResponse,
    RelationshipSuggestionResponse,
    SearchResultResponse,
    WorkspaceSummaryResponse,
)
from ascend.application.uow import UnitOfWork
from ascend.application.workspace.apply_proposal import ApplyProposalUseCase, ConceptProposal, RelationshipProposal
from ascend.application.workspace.get_workspace import GetWorkspaceUseCase
from ascend.application.workspace.search_workspace import SearchWorkspaceUseCase
from ascend.application.workspace.start_guided_capture import StartGuidedCaptureUseCase
from ascend.infrastructure.ai.openrouter import OpenRouterAIService

router = APIRouter(prefix="/workspace", tags=["workspace"])


@router.get("", response_model=WorkspaceSummaryResponse)
def get_workspace_summary(uow: UnitOfWork = Depends(get_uow)):
    use_case = GetWorkspaceUseCase(uow)
    summary = use_case.execute()

    activity_responses = []
    for e in summary.activity:
        activity_responses.append(
            TimelineEventResponse(
                id=e.id,
                aggregate_id=e.aggregate_id,
                aggregate_type=e.aggregate_type,
                event_type=e.event_type,
                occurred_at=e.occurred_at,
                correlation_id=e.correlation_id,
                version=e.version,
                payload=json.loads(e.payload_json),
            )
        )

    pending_proposals_responses = []
    for p in summary.pending_proposals:
        proposal_dict = p["proposal"]
        pending_proposals_responses.append(
            PendingProposalResponse(
                capture_id=p["capture_id"],
                content=p["content"],
                proposal=AIProposalResponse(
                    summary=proposal_dict.get("summary", ""),
                    concepts=[
                        ConceptSuggestionResponse(**c) for c in proposal_dict.get("concepts", [])
                    ],
                    relationships=[
                        RelationshipSuggestionResponse(**r) for r in proposal_dict.get("relationships", [])
                    ],
                    collections=proposal_dict.get("collections", []),
                    review_suggestion=proposal_dict.get("review_suggestion"),
                )
            )
        )

    continue_learning_response = None
    if summary.continue_learning:
        continue_learning_response = ContinueLearningResponse(
            id=summary.continue_learning["id"],
            type=summary.continue_learning["type"],
            title=summary.continue_learning["title"],
            event_type=summary.continue_learning["event_type"],
        )

    daily_stats_response = DailyStatsResponse(
        captures_today=summary.daily_stats["captures_today"],
        reviews_completed_today=summary.daily_stats["reviews_completed_today"],
        concepts_today=summary.daily_stats["concepts_today"],
        pending_proposals=summary.daily_stats["pending_proposals"],
        goal_progress=summary.daily_stats["goal_progress"],
    )

    return WorkspaceSummaryResponse(
        due_reviews=summary.due_reviews,
        recent_captures=[capture_to_response(c) for c in summary.recent_captures],
        pinned_spaces=[to_collection_response(c, uow) for c in summary.pinned_spaces],
        recent_sources=[source_to_response(s) for s in summary.recent_sources],
        activity=activity_responses,
        graph_preview=summary.graph_preview,
        recent_concepts=[concept_to_response(c) for c in summary.recent_concepts],
        recent_collections=[to_collection_response(c, uow) for c in summary.recent_collections],
        pending_proposals=pending_proposals_responses,
        continue_learning=continue_learning_response,
        daily_stats=daily_stats_response,
    )


@router.get("/search", response_model=list[SearchResultResponse])
def search_workspace(q: str, limit: int = 20, uow: UnitOfWork = Depends(get_uow)):
    use_case = SearchWorkspaceUseCase(uow)
    results = use_case.execute(q=q, limit=limit)
    return [
        SearchResultResponse(
            id=r.id,
            type=r.type,
            title=r.title,
            snippet=r.snippet,
        )
        for r in results
    ]


@router.post("/process-capture", response_model=ProcessCaptureResponse)
def process_capture(
    request: ProcessCaptureRequest,
    uow: UnitOfWork = Depends(get_uow)
):
    ai_service = OpenRouterAIService()
    use_case = StartGuidedCaptureUseCase(uow, ai_service)
    capture, response = use_case.execute(request.content)

    return ProcessCaptureResponse(
        capture_id=capture.id,
        proposal=AIProposalResponse(
            summary=response.summary,
            concepts=[
                ConceptSuggestionResponse(name=c.name, description=c.description, confidence=c.confidence)
                for c in response.concepts
            ],
            relationships=[
                RelationshipSuggestionResponse(
                    from_entity=r.from_entity,
                    to_entity=r.to_entity,
                    relationship_type=r.relationship_type,
                    confidence=r.confidence
                )
                for r in response.relationships
            ],
            collections=response.collections,
            review_suggestion=response.review_suggestion,
        )
    )


@router.post("/apply-proposal", status_code=200)
def apply_proposal(
    request: ApplyProposalRequest,
    uow: UnitOfWork = Depends(get_uow)
):
    use_case = ApplyProposalUseCase(uow)
    
    concepts = [
        ConceptProposal(name=c.name, description=c.description, confidence=c.confidence)
        for c in request.proposal.concepts
    ]
    relationships = [
        RelationshipProposal(
            from_entity=r.from_entity,
            to_entity=r.to_entity,
            relationship_type=r.relationship_type,
            confidence=r.confidence
        )
        for r in request.proposal.relationships
    ]

    use_case.execute(
        capture_id=request.capture_id,
        concepts=concepts,
        relationships=relationships,
        collections=request.proposal.collections,
        review_suggestion=request.proposal.review_suggestion,
    )

    return {"status": "success"}
