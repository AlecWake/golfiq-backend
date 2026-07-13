import logging
import re
from time import perf_counter
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.exceptions import unexpected_exception_handler

REQUEST_ID_HEADER = "X-Request-ID"
MAX_REQUEST_ID_LENGTH = 128
SAFE_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]+$")
logger = logging.getLogger("app.requests")


def valid_request_id(header_value: str | None) -> str:
    candidate = header_value.strip() if header_value else ""
    if (candidate and len(candidate) <= MAX_REQUEST_ID_LENGTH
            and SAFE_REQUEST_ID_PATTERN.fullmatch(candidate)):
        return candidate
    return str(uuid4())


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request,
                       call_next: RequestResponseEndpoint) -> Response:
        request_id = valid_request_id(request.headers.get(REQUEST_ID_HEADER))
        request.state.request_id = request_id
        started_at = perf_counter()
        try:
            response = await call_next(request)
        except Exception as exception:
            response = await unexpected_exception_handler(request, exception)

        response.headers[REQUEST_ID_HEADER] = request_id
        elapsed_ms = (perf_counter() - started_at) * 1000
        log_level = (logging.ERROR if response.status_code >= 500 else
                     logging.WARNING if response.status_code >= 400 else logging.INFO)
        logger.log(
            log_level,
            "request_complete request_id=%s method=%s path=%s status_code=%s elapsed_ms=%.2f",
            request_id, request.method, request.url.path, response.status_code, elapsed_ms,
        )
        return response
