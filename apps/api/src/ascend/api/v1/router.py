from fastapi import APIRouter

from ascend.api.v1.endpoints.captures.router import router as captures_router
from ascend.api.v1.endpoints.collections.router import router as collections_router
from ascend.api.v1.endpoints.concepts.router import router as concepts_router
from ascend.api.v1.endpoints.graph.router import router as graph_router
from ascend.api.v1.endpoints.health import router as health_router
from ascend.api.v1.endpoints.relationships.router import router as relationships_router
from ascend.api.v1.endpoints.reviews.router import router as reviews_router
from ascend.api.v1.endpoints.sources.router import router as sources_router
from ascend.api.v1.endpoints.timeline.router import router as timeline_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(captures_router, tags=["captures"])
api_router.include_router(concepts_router, tags=["concepts"])
api_router.include_router(timeline_router, tags=["timeline"])
api_router.include_router(relationships_router, tags=["relationships"])
api_router.include_router(graph_router, tags=["graph"])
api_router.include_router(sources_router, tags=["sources"])
api_router.include_router(collections_router, tags=["collections"])
api_router.include_router(reviews_router, tags=["reviews"])
