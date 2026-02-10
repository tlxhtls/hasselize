"""
Structured logging configuration for Hasselize AI Backend.

Provides JSON-structured logging for production environments.
"""

import logging
import sys
from typing import Any

from pythonjsonlogger import jsonlogger

from .config import settings


class JSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields."""

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        """Add custom fields to log records."""
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record["level"] = record.levelname.lower()
        log_record["logger"] = record.name
        log_record["app"] = settings.app_name
        log_record["version"] = settings.app_version
        log_record["environment"] = settings.environment


def setup_logging() -> logging.Logger:
    """
    Setup application logging.

    Returns:
        Configured root logger instance.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)

    # Use JSON formatter for production, plain text for development
    if settings.json_logs:
        formatter = JSONFormatter(
            fmt="%(asctime)s %(level)s %(logger)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    return root_logger


# Initialize logging on import
logger = setup_logging()
