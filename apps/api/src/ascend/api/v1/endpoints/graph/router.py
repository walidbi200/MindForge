from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from ascend.api.dependencies import get_uow
from ascend.api.v1.endpoints.captures.mappers import to_response as capture_to_response
from ascend.api.v1.endpoints.collections.router import to_collection_response
from ascend.api.v1.endpoints.concepts.router import to_response as concept_to_response
from ascend.api.v1.endpoints.graph.schemas import (
    DuplicateSuggestionResponse,
    GraphResponse,
    KnowledgeNeighborhoodResponse,
    KnowledgeRecommendationResponse,
    NodeResponse,
)
from ascend.api.v1.endpoints.relationships.schemas import RelationshipResponse
from ascend.api.v1.endpoints.sources.router import to_response as source_to_response
from ascend.application.graph.check_duplicates import CheckDuplicatesUseCase
from ascend.application.graph.get_connected_entities import GetConnectedEntitiesUseCase
from ascend.application.graph.get_knowledge_neighborhood import GetKnowledgeNeighborhoodUseCase
from ascend.application.graph.get_relationship_graph import GetRelationshipGraphUseCase
from ascend.application.uow import UnitOfWork
from ascend.domain.relationships.entity import Relationship

router = APIRouter(prefix="/graph")


def _to_relationship_response(rel: Relationship) -> RelationshipResponse:
    return RelationshipResponse(
        id=rel.id,
        from_id=rel.from_id,
        from_type=rel.from_type,
        to_id=rel.to_id,
        to_type=rel.to_type,
        relationship_type=rel.relationship_type,
        confidence=rel.confidence,
        created_by=rel.created_by,
        created_at=rel.created_at,
        metadata_json=rel.metadata_json,
    )


@router.get("/entity/{entity_id}", response_model=list[NodeResponse])
def get_connected_entities(entity_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = GetConnectedEntitiesUseCase(uow)
    nodes = use_case.execute(entity_id)
    return [NodeResponse(id=n.id, type=n.type, title=n.title) for n in nodes]


@router.get("/neighborhood/{entity_id}", response_model=KnowledgeNeighborhoodResponse)
def get_entity_neighborhood(entity_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = GetKnowledgeNeighborhoodUseCase(uow)
    result = use_case.execute(entity_id)
    if not result:
        raise HTTPException(status_code=404, detail="Entity not found in graph")

    center_dict = {}
    if result.center["type"] == "Concept":
        center_dict = concept_to_response(result.center["data"]).model_dump()
        center_dict["entity_type"] = "Concept"
    elif result.center["type"] == "Capture":
        center_dict = capture_to_response(result.center["data"]).model_dump()
        center_dict["entity_type"] = "Capture"
    elif result.center["type"] == "Source":
        center_dict = source_to_response(result.center["data"]).model_dump()
        center_dict["entity_type"] = "Source"

    return KnowledgeNeighborhoodResponse(
        center=center_dict,
        concepts=[concept_to_response(c).model_dump() for c in result.concepts],
        captures=[capture_to_response(c).model_dump() for c in result.captures],
        sources=[source_to_response(s).model_dump() for s in result.sources],
        collections=[to_collection_response(c, uow).model_dump() for c in result.collections],
        relationships=[_to_relationship_response(r) for r in result.relationships],
    )


@router.get("/check-duplicates", response_model=list[DuplicateSuggestionResponse])
def check_duplicates(title: str, exclude_id: UUID | None = None, uow: UnitOfWork = Depends(get_uow)):
    use_case = CheckDuplicatesUseCase(uow)
    suggestions = use_case.execute(title, exclude_id)
    return [
        DuplicateSuggestionResponse(
            concept_id=s.concept.id,
            title=s.concept.title,
            similarity_score=s.similarity_score,
            reason=s.reason,
        )
        for s in suggestions
    ]


@router.get("/path-preview/{entity_id}", response_model=GraphResponse)
def get_path_preview(entity_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    # Path preview could mean depth 2
    use_case = GetRelationshipGraphUseCase(uow)
    nodes, relationships = use_case.execute(entity_id, depth=2, max_nodes=50)

    return GraphResponse(
        nodes=[NodeResponse(id=n.id, type=n.type, title=n.title) for n in nodes],
        relationships=[_to_relationship_response(r) for r in relationships],
    )


@router.get("/recommendations/{entity_id}", response_model=list[KnowledgeRecommendationResponse])
def get_recommendations(entity_id: UUID, limit: int = 5, uow: UnitOfWork = Depends(get_uow)):
    from ascend.application.graph.get_recommendations import GetKnowledgeRecommendationsUseCase
    use_case = GetKnowledgeRecommendationsUseCase(uow)
    results = use_case.execute(entity_id, limit)
    from ascend.api.v1.endpoints.graph.schemas import KnowledgeRecommendationResponse
    return [
        KnowledgeRecommendationResponse(
            id=r.id,
            type=r.type,
            title=r.title,
            reason=r.reason,
            score=r.score,
        )
        for r in results
    ]
