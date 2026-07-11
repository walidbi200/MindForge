from uuid import UUID

from fastapi import APIRouter, Depends

from ascend.api.dependencies import get_uow
from ascend.api.v1.endpoints.graph.schemas import GraphResponse, NodeResponse
from ascend.api.v1.endpoints.relationships.schemas import RelationshipResponse
from ascend.application.graph.get_connected_entities import GetConnectedEntitiesUseCase
from ascend.application.graph.get_entity_neighborhood import GetEntityNeighborhoodUseCase
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


@router.get("/neighborhood/{entity_id}", response_model=GraphResponse)
def get_entity_neighborhood(entity_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = GetEntityNeighborhoodUseCase(uow)
    nodes, relationships = use_case.execute(entity_id)

    return GraphResponse(
        nodes=[NodeResponse(id=n.id, type=n.type, title=n.title) for n in nodes],
        relationships=[_to_relationship_response(r) for r in relationships],
    )


@router.get("/path-preview/{entity_id}", response_model=GraphResponse)
def get_path_preview(entity_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    # Path preview could mean depth 2
    use_case = GetRelationshipGraphUseCase(uow)
    nodes, relationships = use_case.execute(entity_id, depth=2, max_nodes=50)

    return GraphResponse(
        nodes=[NodeResponse(id=n.id, type=n.type, title=n.title) for n in nodes],
        relationships=[_to_relationship_response(r) for r in relationships],
    )
