"""Structured logging configuration for Quote of the Day API."""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import structlog
from structlog.types import Processor

from src.core.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id

        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id

        if hasattr(record, 'trace_id'):
            log_entry['trace_id'] = record.trace_id

        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        # Add any extra attributes
        for key, value in record.__dict__.items():
            if key not in [
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                'thread', 'threadName', 'processName', 'process', 'getMessage'
            ]:
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


def add_environment_info(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add environment information to log entries."""
    event_dict['environment'] = settings.ENVIRONMENT
    event_dict['service'] = 'quote-api'
    return event_dict


def add_request_id(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add request ID if available in context."""
    # This would typically get the request ID from context
    # For now, we'll just pass through
    return event_dict


def configure_structlog():
    """Configure structlog for structured logging."""
    processors: list[Processor] = [
        # Add environment and service info
        add_environment_info,
        add_request_id,
        # Add timestamp
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.is_development:
        # Pretty console output for development
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True)
        ])
    else:
        # JSON output for production
        processors.extend([
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ])

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )


def setup_logging() -> None:
    """Set up application logging configuration."""
    # Configure structlog
    configure_structlog()

    # Set logging level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if settings.is_production:
        # Use JSON formatter for production
        console_handler.setFormatter(JSONFormatter())
    else:
        # Use simple formatter for development
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)

    # Configure specific loggers
    loggers_config = {
        'uvicorn': logging.INFO,
        'uvicorn.error': logging.INFO,
        'uvicorn.access': logging.WARNING if settings.is_production else logging.INFO,
        'sqlalchemy.engine': logging.WARNING if settings.is_production else logging.INFO,
        'alembic': logging.INFO,
        'quote': log_level,
    }

    for logger_name, level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

    # Disable some noisy loggers in production
    if settings.is_production:
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('botocore').setLevel(logging.WARNING)
        logging.getLogger('boto3').setLevel(logging.WARNING)

    # Create application logger
    app_logger = structlog.get_logger("quote.api")
    app_logger.info(
        "Logging configured",
        level=settings.LOG_LEVEL,
        environment=settings.ENVIRONMENT,
        structured=settings.is_production
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class RequestLoggingMiddleware:
    """Middleware to add request logging and context."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        """Process request with logging context."""
        if scope["type"] == "http":
            import uuid
            from contextvars import ContextVar

            # Create request ID
            request_id = str(uuid.uuid4())

            # Set up logging context
            logger = get_logger("quote.api.request")

            # Log request start
            logger.info(
                "Request started",
                request_id=request_id,
                method=scope["method"],
                path=scope["path"],
                client_ip=scope.get("client", ["unknown"])[0]
            )

            # Store request ID in context
            request_id_var: ContextVar[str] = ContextVar('request_id', default='')
            request_id_var.set(request_id)

            async def send_with_logging(message):
                if message["type"] == "http.response.start":
                    status_code = message["status"]
                    logger.info(
                        "Request completed",
                        request_id=request_id,
                        status_code=status_code,
                        method=scope["method"],
                        path=scope["path"]
                    )
                await send(message)

            await self.app(scope, receive, send_with_logging)
        else:
            await self.app(scope, receive, send)