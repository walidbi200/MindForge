from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from ascend.api.dependencies import get_uow
from ascend.api.v1.endpoints.relationships.schemas import CreateRelationshipRequest, RelationshipResponse
from ascend.application.relationships.create_relationship import CreateRelationshipUseCase
from ascend.application.relationships.delete_relationship import DeleteRelationshipUseCase
from ascend.application.relationships.get_relationship import GetRelationshipUseCase
from ascend.application.relationships.list_relationships import (
    ListIncomingRelationshipsUseCase,
    ListOutgoingRelationshipsUseCase,
)
from ascend.application.uow import UnitOfWork
from ascend.domain.relationships.entity import Relationship

router = APIRouter(prefix="/relationships")


def to_response(rel: Relationship) -> RelationshipResponse:
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


@router.post("", response_model=RelationshipResponse, status_code=status.HTTP_201_CREATED)
def create_relationship(request: CreateRelationshipRequest, uow: UnitOfWork = Depends(get_uow)):
    use_case = CreateRelationshipUseCase(uow)
    try:
        relationship = use_case.execute(
            relationship_id=uuid4(),
            from_id=request.from_id,
            from_type=request.from_type,
            to_id=request.to_id,
            to_type=request.to_type,
            relationship_type=request.relationship_type,
            confidence=request.confidence,
            created_by=request.created_by,
            metadata_dict=request.metadata_dict,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    return to_response(relationship)


@router.get("/{relationship_id}", response_model=RelationshipResponse)
def get_relationship(relationship_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = GetRelationshipUseCase(uow)
    relationship = use_case.execute(relationship_id)
    if not relationship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")
    return to_response(relationship)


@router.delete("/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relationship(relationship_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = DeleteRelationshipUseCase(uow)
    success = use_case.execute(relationship_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")


@router.get("/entity/{entity_id}/outgoing", response_model=list[RelationshipResponse])
def list_outgoing_relationships(entity_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = ListOutgoingRelationshipsUseCase(uow)
    relationships = use_case.execute(entity_id)
    return [to_response(rel) for rel in relationships]


@router.get("/entity/{entity_id}/incoming", response_model=list[RelationshipResponse])
def list_incoming_relationships(entity_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = ListIncomingRelationshipsUseCase(uow)
    relationships = use_case.execute(entity_id)
    return [to_response(rel) for rel in relationships]
