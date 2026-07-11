from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from ascend.application.uow import UnitOfWork
from ascend.api.dependencies import get_uow
from ascend.api.v1.endpoints.captures.schemas import CreateCaptureRequest, CaptureResponse
from ascend.api.v1.endpoints.captures.mappers import to_response
from ascend.application.captures.create_capture import CreateCaptureUseCase
from ascend.application.captures.get_capture import GetCaptureUseCase

router = APIRouter(prefix="/captures", tags=["captures"])

@router.post("", response_model=CaptureResponse, status_code=status.HTTP_201_CREATED)
async def create_capture(
    request: CreateCaptureRequest,
    uow: UnitOfWork = Depends(get_uow)
) -> CaptureResponse:
    use_case = CreateCaptureUseCase(uow)
    capture = use_case.execute(request.content)
    return to_response(capture)

@router.get("/{capture_id}", response_model=CaptureResponse)
async def get_capture(
    capture_id: UUID,
    uow: UnitOfWork = Depends(get_uow)
) -> CaptureResponse:
    use_case = GetCaptureUseCase(uow)
    capture = use_case.execute(capture_id)
    if not capture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capture not found")
    return to_response(capture)
