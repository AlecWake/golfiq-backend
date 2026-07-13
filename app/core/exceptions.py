import logging
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.error import ErrorResponse

logger = logging.getLogger("app.errors")


def get_request_id(request: Request) -> str:
    request_id = getattr(request.state, "request_id", None)
    if request_id is None:
        request_id = str(uuid4())
        request.state.request_id = request_id
    return request_id


def error_response(request: Request, status_code: int, code: str, message: str,
                   details: Any | None = None,
                   headers: dict[str, str] | None = None) -> JSONResponse:
    request_id = get_request_id(request)
    payload = ErrorResponse(
        error={"code": code, "message": message, "details": details},
        request_id=request_id,
    )
    response = JSONResponse(status_code=status_code,
                            content=payload.model_dump(mode="json"), headers=headers)
    response.headers["X-Request-ID"] = request_id
    return response


def _http_error_code(status_code: int) -> str:
    return {401: "invalid_authentication_credentials", 403: "authorization_denied",
            404: "resource_not_found", 409: "resource_conflict"}.get(
        status_code, "http_error"
    )


async def http_exception_handler(request: Request,
                                 exception: HTTPException) -> JSONResponse:
    message = exception.detail if isinstance(exception.detail, str) else "Request failed."
    details = None if isinstance(exception.detail, str) else exception.detail
    return error_response(request, exception.status_code,
                          _http_error_code(exception.status_code), message, details,
                          exception.headers)


async def validation_exception_handler(
    request: Request, exception: RequestValidationError
) -> JSONResponse:
    details = [{"field": ".".join(str(part) for part in error["loc"]),
                "message": error["msg"], "type": error["type"]}
               for error in exception.errors()]
    return error_response(request, 422, "validation_error",
                          "Request validation failed.", details)


async def unexpected_exception_handler(request: Request,
                                       exception: Exception) -> JSONResponse:
    request_id = get_request_id(request)
    logger.exception(
        "unexpected_request_error request_id=%s method=%s path=%s",
        request_id, request.method, request.url.path, exc_info=exception,
    )
    return error_response(request, 500, "internal_server_error",
                          "An unexpected error occurred.")
