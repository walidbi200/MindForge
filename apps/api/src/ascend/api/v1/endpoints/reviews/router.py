from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, status

from ascend.api.dependencies import get_uow
from ascend.api.v1.endpoints.reviews.schemas import (
    CompleteReviewRequest,
    CreateReviewRequest,
    ReviewResponse,
)
from ascend.application.reviews.complete_review import CompleteReviewUseCase
from ascend.application.reviews.create_review import CreateReviewUseCase
from ascend.application.reviews.delete_review import DeleteReviewUseCase
from ascend.application.reviews.get_review import GetReviewUseCase
from ascend.application.reviews.list_due_reviews import ListDueReviewsUseCase
from ascend.application.reviews.list_entity_reviews import ListEntityReviewsUseCase
from ascend.application.reviews.skip_review import SkipReviewUseCase
from ascend.application.uow import UnitOfWork
from ascend.domain.exceptions import EntityNotFoundError

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(request: CreateReviewRequest, uow: UnitOfWork = Depends(get_uow)):
    use_case = CreateReviewUseCase(uow)
    review = use_case.execute(
        review_id=uuid4(),
        entity_id=request.entity_id,
        entity_type=request.entity_type,
        due_at=request.due_at,
        metadata_json=request.metadata_json,
    )
    return review


@router.get("/due", response_model=list[ReviewResponse])
def list_due_reviews(uow: UnitOfWork = Depends(get_uow)):
    use_case = ListDueReviewsUseCase(uow)
    return use_case.execute()


@router.get("/entity/{entity_id}", response_model=list[ReviewResponse])
def list_entity_reviews(entity_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = ListEntityReviewsUseCase(uow)
    return use_case.execute(entity_id)


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(review_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = GetReviewUseCase(uow)
    review = use_case.execute(review_id)
    if not review:
        raise EntityNotFoundError("Review not found")
    return review


@router.post("/{review_id}/complete", response_model=ReviewResponse)
def complete_review(review_id: UUID, request: CompleteReviewRequest, uow: UnitOfWork = Depends(get_uow)):
    use_case = CompleteReviewUseCase(uow)
    return use_case.execute(review_id, request.metadata_json)


@router.post("/{review_id}/skip", response_model=ReviewResponse)
def skip_review(review_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = SkipReviewUseCase(uow)
    return use_case.execute(review_id)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = DeleteReviewUseCase(uow)
    success = use_case.execute(review_id)
    if not success:
        raise EntityNotFoundError("Review not found")
