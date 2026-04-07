from fastapi import Security
from fastapi.security import APIKeyHeader

from app.core.config import config
from app.core.exceptions import IngemarkUnauthorizedError

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(_api_key_header)) -> str:
    """FastAPI dependency that validates API key from X-API-Key header.

    Usage in router:
        @router.get("/", dependencies=[Depends(verify_api_key)])
    """
    if not api_key or api_key != config.AUTH.api_key:
        raise IngemarkUnauthorizedError("Invalid or missing API key")
    return api_key
