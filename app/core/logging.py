import logging

from app.core.config import settings


def configure_logging() -> None:
    """Configure GolfIQ loggers without adding duplicate output handlers."""
    logging.getLogger("app").setLevel(settings.log_level.upper())
