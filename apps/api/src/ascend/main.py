"""Application entrypoint for the Ascend API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ascend.core.settings import settings
from ascend.core.logging import setup_logging
from ascend.core.errors import setup_error_handlers
from ascend.api.v1.router import api_router

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    setup_logging()
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="API foundation for Ascend.",
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    setup_error_handlers(app)
    
    app.include_router(api_router, prefix="/api/v1")
    
    return app

app = create_app()
