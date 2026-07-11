import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from ascend.domain.exceptions import ConflictError, DomainException, IntegrityError, NotFoundError, ValidationError

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning("Validation error: %s", exc.errors())
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "message": "Validation failed", "details": exc.errors()}},
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    logger.warning("HTTP error %d: %s", exc.status_code, exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": "HTTP_ERROR", "message": exc.detail}})


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    logger.warning("Domain error: %s", str(exc))

    if isinstance(exc, NotFoundError):
        status_code = 404
        code = "NOT_FOUND"
    elif isinstance(exc, ConflictError):
        status_code = 409
        code = "CONFLICT"
    elif isinstance(exc, IntegrityError):
        status_code = 409
        code = "INTEGRITY_ERROR"
    elif isinstance(exc, ValidationError):
        status_code = 422
        code = "VALIDATION_ERROR"
    else:
        status_code = 400
        code = "BAD_REQUEST"

    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": str(exc)}},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception occurred: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred."}},
    )


def setup_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(DomainException, domain_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
