from fastapi import APIRouter
from pydantic import BaseModel
from ascend.core.settings import settings

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="mindforge-api",
        version=settings.VERSION
    )
