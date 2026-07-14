from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.api.openapi import API_DESCRIPTION, API_VERSION, CONTACT, OPENAPI_TAGS
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
        title="GolfIQ API",
        summary="Practice-to-course golf performance intelligence.",
        description=API_DESCRIPTION,
        version=API_VERSION,
        contact=CONTACT,
        openapi_tags=OPENAPI_TAGS,
        docs_url="/docs",
        redoc_url="/redoc",
        swagger_ui_parameters={
            "deepLinking": True,
            "displayRequestDuration": True,
            "docExpansion": "none",
            "filter": True,
            "persistAuthorization": True,
        },
    )
    application.add_middleware(RequestContextMiddleware)
    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)
    application.add_exception_handler(Exception, unexpected_exception_handler)
    application.include_router(api_router, prefix="/api/v1")
    return application


app = create_app()
