from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ascend.api.dependencies import get_uow
from ascend.api.v1.endpoints.reviews.schemas import (
    CompleteReviewRequest,
    CreateReviewRequest,
    ReviewResponse,
    UpdateReviewRequest,
)
from ascend.application.reviews.complete_review import CompleteReviewUseCase
from ascend.application.reviews.create_review import CreateReviewUseCase
from ascend.application.reviews.delete_review import DeleteReviewUseCase
from ascend.application.reviews.get_review import GetReviewUseCase
from ascend.application.reviews.list_due_reviews import ListDueReviewsUseCase
from ascend.application.reviews.list_reviews import ListReviewsUseCase
from ascend.application.reviews.update_review import UpdateReviewUseCase
from ascend.application.uow import UnitOfWork
from ascend.domain.reviews.entity import Review

router = APIRouter(prefix="/reviews")


def to_review_response(r: Review) -> ReviewResponse:
    return ReviewResponse(
        id=r.id,
        entity_id=r.entity_id,
        entity_type=r.entity_type,
        review_type=r.review_type,
        status=r.status,
        difficulty=r.difficulty,
        score=r.score,
        notes=r.notes,
        created_at=r.created_at,
        updated_at=r.updated_at,
        last_reviewed_at=r.last_reviewed_at,
        next_review_at=r.next_review_at,
    )


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(request: CreateReviewRequest, uow: UnitOfWork = Depends(get_uow)):
    use_case = CreateReviewUseCase(uow)
    try:
        review = use_case.execute(
            review_id=uuid4(),
            entity_id=request.entity_id,
            entity_type=request.entity_type,
            review_type=request.review_type,
            difficulty=request.difficulty,
            notes=request.notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return to_review_response(review)


@router.get("/due", response_model=list[ReviewResponse])
def get_due_reviews(uow: UnitOfWork = Depends(get_uow)):
    use_case = ListDueReviewsUseCase(uow)
    reviews = use_case.execute()
    return [to_review_response(r) for r in reviews]


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(review_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = GetReviewUseCase(uow)
    review = use_case.execute(review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return to_review_response(review)


@router.patch("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: UUID, request: UpdateReviewRequest, uow: UnitOfWork = Depends(get_uow)
):
    use_case = UpdateReviewUseCase(uow)
    review = use_case.execute(
        review_id=review_id,
        status=request.status,
        difficulty=request.difficulty,
        score=request.score,
        notes=request.notes,
        next_review_at=request.next_review_at,
    )
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return to_review_response(review)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    use_case = DeleteReviewUseCase(uow)
    success = use_case.execute(review_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")


@router.post("/{review_id}/complete", response_model=ReviewResponse)
def complete_review(
    review_id: UUID, request: CompleteReviewRequest, uow: UnitOfWork = Depends(get_uow)
):
    use_case = CompleteReviewUseCase(uow)
    try:
        review = use_case.execute(
            review_id=review_id,
            difficulty=request.difficulty,
            score=request.score,
            notes=request.notes,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    return to_review_response(review)


@router.get("", response_model=list[ReviewResponse])
def list_reviews(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    uow: UnitOfWork = Depends(get_uow),
):
    use_case = ListReviewsUseCase(uow)
    reviews = use_case.execute(offset=offset, limit=limit)
    return [to_review_response(r) for r in reviews]
