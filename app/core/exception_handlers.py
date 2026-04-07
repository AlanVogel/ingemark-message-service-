import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import IngemarkBaseError

logger = logging.getLogger(__name__)


async def ingemark_exception_handler(request: Request, exc: IngemarkBaseError) -> JSONResponse:
    """Handle all custom Ingemark exceptions with consistent JSON response."""
    logger.warning(f"{exc.__class__.__name__}: {exc.message} | path={request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions. Prevents stack traces leaking to client."""
    logger.error(f"Unhandled exception: {exc} | path={request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
