import logging
from contextvars import ContextVar

# Context variable to store the correlation ID per request
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="-")


class CorrelationIdFilter(logging.Filter):
    """Injects the current correlation ID into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id.get()
        return True


def setup_logging() -> None:
    """Configure application-wide logging with correlation ID support."""
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(correlation_id)s | %(name)s | %(message)s"
        )
    )
    handler.addFilter(CorrelationIdFilter())

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger. Correlation ID is injected automatically."""
    return logging.getLogger(name)
