from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

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
    },
)
async def health(db: Session = Depends(get_db)) -> dict:
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return {"status": "unhealthy", "database": "disconnected"}
