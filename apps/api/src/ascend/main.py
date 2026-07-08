"""Application entrypoint for the Ascend API."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    return FastAPI(
        title="Ascend API",
        version="0.0.1",
        description="API foundation for Ascend.",
    )


app = create_app()

