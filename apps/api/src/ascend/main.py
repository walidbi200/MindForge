"""Application entrypoint for the Ascend API."""

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ascend.api.v1.router import api_router
from ascend.core.errors import setup_error_handlers
from ascend.core.logging import setup_logging
from ascend.core.settings import settings

# Initialize Sentry before the app is created so all exceptions are captured.
# Disabled when SENTRY_DSN is empty (local dev or test environments).
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1,
    )


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
