from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from ascend.api.dependencies import get_uow
from ascend.api.v1.endpoints.collections.schemas import (
    AddEntityRequest,
    CollectionResponse,
    CreateCollectionRequest,
    MembershipResponse,
    UpdateCollectionRequest,
)
from ascend.api.v1.endpoints.graph.schemas import NodeResponse
from ascend.application.collections.add_entity_to_collection import AddEntityToCollectionUseCase
from ascend.application.collections.create_collection import CreateCollectionUseCase
from ascend.application.collections.delete_collection import DeleteCollectionUseCase
from ascend.application.collections.get_collection import GetCollectionUseCase
from ascend.application.collections.list_collection_entities import ListCollectionEntitiesUseCase
from ascend.application.collections.list_collections import ListCollectionsUseCase
from ascend.application.collections.list_entity_collections import ListEntityCollectionsUseCase
from ascend.application.collections.remove_entity_from_collection import RemoveEntityFromCollectionUseCase
from ascend.application.collections.update_collection import UpdateCollectionUseCase
from ascend.application.uow import UnitOfWork
from ascend.domain.collections.entity import Collection, Membership

router = APIRouter(prefix="/collections")


def to_collection_response(c: Collection) -> CollectionResponse:
    return CollectionResponse(
        id=c.id,
        name=c.name,
        description=c.description,
        color=c.color,
        icon=c.icon,
        created_at=c.created_at,
        updated_at=c.updated_at,
        metadata_json=c.metadata_json,
    )


def to_membership_response(m: Membership) -> MembershipResponse:
    return MembershipResponse(
        id=m.id,
        collection_id=m.collection_id,
        entity_id=m.entity_id,
        entity_type=m.entity_type,
        created_at=m.created_at,
    )


@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection(request: CreateCollectionRequest, uow: UnitOfWork = Depends(get_uow)):
    use_case = CreateCollectionUseCase(uow)
    try:
        collection = use_case.execute(
            collection_id=uuid4(),
            name=request.name,
            description=request.description,
            color=request.color,
            icon=request.icon,
            metadata_json=request.metadata_json,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return to_collection_response(collection)


@router.get("/{collection_id}", response_model=CollectionResponse)
def get_collection(collection_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = GetCollectionUseCase(uow)
    collection = use_case.execute(collection_id)
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return to_collection_response(collection)


@router.patch("/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: UUID, request: UpdateCollectionRequest, uow: UnitOfWork = Depends(get_uow)
):
    use_case = UpdateCollectionUseCase(uow)
    try:
        collection = use_case.execute(
            collection_id=collection_id,
            name=request.name,
            description=request.description,
            color=request.color,
            icon=request.icon,
            metadata_json=request.metadata_json,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return to_collection_response(collection)


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(collection_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = DeleteCollectionUseCase(uow)
    try:
        success = use_case.execute(collection_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")


@router.get("", response_model=list[CollectionResponse])
def list_collections(uow: UnitOfWork = Depends(get_uow)):
    use_case = ListCollectionsUseCase(uow)
    collections = use_case.execute()
    return [to_collection_response(c) for c in collections]


@router.post("/{collection_id}/entities", response_model=MembershipResponse, status_code=status.HTTP_201_CREATED)
def add_entity_to_collection(
    collection_id: UUID, request: AddEntityRequest, uow: UnitOfWork = Depends(get_uow)
):
    use_case = AddEntityToCollectionUseCase(uow)
    try:
        membership = use_case.execute(
            membership_id=uuid4(),
            collection_id=collection_id,
            entity_id=request.entity_id,
            entity_type=request.entity_type,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return to_membership_response(membership)


@router.delete("/{collection_id}/entities/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_entity_from_collection(
    collection_id: UUID, entity_id: UUID, uow: UnitOfWork = Depends(get_uow)
):
    use_case = RemoveEntityFromCollectionUseCase(uow)
    success = use_case.execute(collection_id, entity_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Membership mapping not found"
        )


@router.get("/{collection_id}/entities", response_model=list[NodeResponse])
def list_collection_entities(collection_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = ListCollectionEntitiesUseCase(uow)
    nodes = use_case.execute(collection_id)
    return [NodeResponse(id=n.id, type=n.type, title=n.title) for n in nodes]


@router.get("/entity/{entity_id}", response_model=list[CollectionResponse])
def list_entity_collections(entity_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = ListEntityCollectionsUseCase(uow)
    collections = use_case.execute(entity_id)
    return [to_collection_response(c) for c in collections]
