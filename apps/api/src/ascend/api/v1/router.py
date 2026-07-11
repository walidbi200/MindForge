from fastapi import APIRouter
from ascend.api.v1.endpoints.health import router as health_router
from ascend.api.v1.endpoints.captures.router import router as captures_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(captures_router, tags=["captures"])
