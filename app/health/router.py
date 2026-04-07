from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Health check",
    description="Verifies the application is running and the database is reachable.",
    responses={
        200: {
            "description": "Service is healthy.",
            "content": {
                "application/json": {"example": {"status": "healthy", "database": "connected"}}
            },
        },
        503: {
            "description": "Service is unhealthy.",
            "content": {
                "application/json": {"example": {"status": "unhealthy", "database": "disconnected"}}
            },
        },
    },
)
async def health(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    try:
        await db.execute(text("SELECT 1"))
        return JSONResponse(
            status_code=200,
            content={"status": "healthy", "database": "connected"},
        )
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected"},
        )
