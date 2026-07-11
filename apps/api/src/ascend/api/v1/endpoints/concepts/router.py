from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from ascend.api.dependencies import get_uow
from ascend.api.v1.endpoints.concepts.schemas import ConceptResponse, CreateConceptRequest
from ascend.application.concepts.create_concept import CreateConceptUseCase
from ascend.application.concepts.delete_concept import DeleteConceptUseCase
from ascend.application.concepts.get_concept import GetConceptUseCase
from ascend.application.uow import UnitOfWork
from ascend.domain.concepts.entity import Concept

router = APIRouter(prefix="/concepts")


def to_response(concept: Concept) -> ConceptResponse:
    return ConceptResponse(
        id=concept.id,
        title=concept.title,
        summary=concept.summary,
        created_at=concept.created_at,
        updated_at=concept.updated_at,
    )


@router.post("", response_model=ConceptResponse, status_code=status.HTTP_201_CREATED)
def create_concept(request: CreateConceptRequest, uow: UnitOfWork = Depends(get_uow)):
    use_case = CreateConceptUseCase(uow)
    concept = use_case.execute(uuid4(), request.title, request.summary)
    return to_response(concept)


@router.get("/{concept_id}", response_model=ConceptResponse)
def get_concept(concept_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = GetConceptUseCase(uow)
    concept = use_case.execute(concept_id)
    if not concept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concept not found")
    return to_response(concept)


@router.delete("/{concept_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_concept(concept_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = DeleteConceptUseCase(uow)
    success = use_case.execute(concept_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concept not found")
