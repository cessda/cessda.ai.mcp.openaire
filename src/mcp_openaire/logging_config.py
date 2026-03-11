# SPDX-License-Identifier: Apache-2.0
"""Structured JSON logging configuration.

Logs to stdout in JSON format with:
- Single-line JSON messages
- Parameterized logging for performance
- Context information (operation, objects, reason)
- Default WARN level
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional


class StructuredJSONFormatter(logging.Formatter):
    """JSON formatter for structured logging to stdout.

    Outputs single-line JSON with timestamp, level, message, and context.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as single-line JSON.

        Args:
            record: Log record to format

        Returns:
            Single-line JSON string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Add context fields if present
        if hasattr(record, "context"):
            log_data.update(record.context)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
                "context",
            ]:
                log_data[key] = value

        return json.dumps(log_data)


def setup_logging(level: Optional[str] = None) -> logging.Logger:
    """Configure structured JSON logging to stdout.

    Args:
        level: Log level (defaults to WARN)

    Returns:
        Configured logger instance
    """
    from .config import config

    log_level = level or config.log_level

    # Create logger
    logger = logging.getLogger("mcp_openaire")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Create stdout handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJSONFormatter())
    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **context: Any
) -> None:
    """Log message with additional context fields.

    Args:
        logger: Logger instance
        level: Log level (INFO, WARN, ERROR, etc.)
        message: Log message
        **context: Additional context fields
    """
    log_method = getattr(logger, level.lower())
    extra = {"context": context} if context else {}
    log_method(message, extra=extra)


# Global logger instance
logger = setup_logging()
