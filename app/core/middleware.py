import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logger import correlation_id, get_logger

logger = get_logger(__name__)

CORRELATION_HEADER = "X-Correlation-ID"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Assigns a unique correlation ID to each request.

    If the client sends an X-Correlation-ID header, it is reused.
    Otherwise, a new UUID is generated. The ID is included in the response
    headers and attached to all log messages for the request.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get(CORRELATION_HEADER, str(uuid.uuid4()))
        token = correlation_id.set(request_id)

        logger.info("%s %s", request.method, request.url.path)

        try:
            response = await call_next(request)
            response.headers[CORRELATION_HEADER] = request_id
            logger.info("%s %s -> %s", request.method, request.url.path, response.status_code)
            return response
        finally:
            correlation_id.reset(token)
