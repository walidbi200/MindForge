from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from ascend.api.dependencies import get_uow
from ascend.api.v1.endpoints.sources.schemas import CreateSourceRequest, SourceResponse, UpdateSourceRequest
from ascend.application.sources.create_source import CreateSourceUseCase
from ascend.application.sources.delete_source import DeleteSourceUseCase
from ascend.application.sources.get_source import GetSourceUseCase
from ascend.application.sources.list_sources import ListSourcesUseCase
from ascend.application.sources.update_source import UpdateSourceUseCase
from ascend.application.uow import UnitOfWork
from ascend.domain.sources.entity import Source, SourceType

router = APIRouter(prefix="/sources")


def to_response(source: Source) -> SourceResponse:
    return SourceResponse(
        id=source.id,
        title=source.title,
        source_type=source.source_type,
        uri=source.uri,
        author=source.author,
        publisher=source.publisher,
        language=source.language,
        created_at=source.created_at,
        updated_at=source.updated_at,
        metadata_json=source.metadata_json,
    )


@router.post("", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
def create_source(request: CreateSourceRequest, uow: UnitOfWork = Depends(get_uow)):
    use_case = CreateSourceUseCase(uow)
    source = use_case.execute(
        source_id=uuid4(),
        title=request.title,
        source_type=request.source_type,
        uri=request.uri,
        author=request.author,
        publisher=request.publisher,
        language=request.language,
        metadata_json=request.metadata_json,
    )
    return to_response(source)


@router.get("/{source_id}", response_model=SourceResponse)
def get_source(source_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = GetSourceUseCase(uow)
    source = use_case.execute(source_id)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    return to_response(source)


@router.patch("/{source_id}", response_model=SourceResponse)
def update_source(source_id: UUID, request: UpdateSourceRequest, uow: UnitOfWork = Depends(get_uow)):
    use_case = UpdateSourceUseCase(uow)
    try:
        source = use_case.execute(
            source_id=source_id,
            title=request.title,
            source_type=request.source_type,
            uri=request.uri,
            author=request.author,
            publisher=request.publisher,
            language=request.language,
            metadata_json=request.metadata_json,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    return to_response(source)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(source_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = DeleteSourceUseCase(uow)
    try:
        success = use_case.execute(source_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")


@router.get("", response_model=list[SourceResponse])
def list_sources(
    limit: int = 50,
    offset: int = 0,
    source_type: SourceType | None = None,
    uow: UnitOfWork = Depends(get_uow),
):
    use_case = ListSourcesUseCase(uow)
    sources = use_case.execute(limit=limit, offset=offset, source_type=source_type)
    return [to_response(s) for s in sources]
