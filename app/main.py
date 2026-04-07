import logging

from fastapi import FastAPI

from app.core.exception_handlers import ingemark_exception_handler, unhandled_exception_handler
from app.core.exceptions import IngemarkBaseError
from app.health.router import router as health_router
from app.messages.router import router as messages_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

app = FastAPI(
    title="Ingemark Message Service",
    description="Message persistence service for AI assistant system",
    version="0.1.0",
)

# Exception handlers
app.add_exception_handler(IngemarkBaseError, ingemark_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Routers
app.include_router(health_router)
app.include_router(messages_router, prefix="/api/v1")
