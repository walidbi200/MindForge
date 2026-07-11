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

@router.get("/health/db", response_model=HealthResponse)
async def get_health_db() -> HealthResponse:
    from ascend.infrastructure.database import engine
    from sqlmodel import text
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
        
    return HealthResponse(
        status=db_status,
        service="mindforge-api-db",
        version=settings.VERSION
    )
