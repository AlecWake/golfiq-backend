from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.api.router import api_router
from app.core.exceptions import (
    http_exception_handler,
    unexpected_exception_handler,
    validation_exception_handler,
)
from app.core.logging import configure_logging
from app.middleware.request_context import RequestContextMiddleware


def create_app() -> FastAPI:
    configure_logging()
    application = FastAPI(
        title="GolfIQ Backend",
        description="Practice-to-course transfer analytics platform for golfers.",
        version="0.1.0",
    )
    application.add_middleware(RequestContextMiddleware)
    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)
    application.add_exception_handler(Exception, unexpected_exception_handler)
    application.include_router(api_router, prefix="/api/v1")
    return application


app = create_app()
