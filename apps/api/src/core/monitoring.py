"""Application monitoring and error tracking configuration."""

import logging
from typing import Optional
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration

from src.core.config import settings

logger = logging.getLogger(__name__)


def setup_sentry() -> None:
    """Configure Sentry error tracking."""
    if not settings.SENTRY_DSN:
        logger.info("Sentry DSN not configured, skipping Sentry setup")
        return

    # Configure Sentry integrations
    integrations = [
        FastApiIntegration(auto_enabling_integrations=True),
        SqlalchemyIntegration(),
        RedisIntegration(),
        AsyncioIntegration(),
        LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        ),
    ]

    # Configure sample rates based on environment
    if settings.is_production:
        traces_sample_rate = 0.1  # 10% for production
        profiles_sample_rate = 0.1  # 10% for production
    elif settings.ENVIRONMENT == "staging":
        traces_sample_rate = 0.5  # 50% for staging
        profiles_sample_rate = 0.5  # 50% for staging
    else:
        traces_sample_rate = 1.0  # 100% for development
        profiles_sample_rate = 1.0  # 100% for development

    # Initialize Sentry
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=integrations,
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        environment=settings.ENVIRONMENT,
        release=f"quote-api@1.0.0",
        send_default_pii=False,  # Don't send personally identifiable information
        attach_stacktrace=True,
        max_breadcrumbs=50,
        debug=settings.DEBUG,
        before_send=filter_sensitive_data,
    )

    # Set user context
    sentry_sdk.set_context("application", {
        "name": "quote-api",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    })

    logger.info(
        "Sentry configured successfully",
        environment=settings.ENVIRONMENT,
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate
    )


def filter_sensitive_data(event, hint):
    """Filter out sensitive data from Sentry events."""
    # Remove sensitive headers
    if 'request' in event and 'headers' in event['request']:
        sensitive_headers = {'authorization', 'x-api-key', 'cookie', 'set-cookie'}
        headers = event['request']['headers']
        for header in list(headers.keys()):
            if header.lower() in sensitive_headers:
                headers[header] = '[Filtered]'

    # Remove sensitive query parameters
    if 'request' in event and 'query_string' in event['request']:
        query_string = event['request']['query_string']
        if 'password' in query_string or 'token' in query_string:
            event['request']['query_string'] = '[Filtered]'

    # Remove sensitive form data
    if 'request' in event and 'data' in event['request']:
        data = event['request']['data']
        if isinstance(data, dict):
            sensitive_fields = {'password', 'secret', 'token', 'api_key'}
            for field in sensitive_fields:
                if field in data:
                    data[field] = '[Filtered]'

    return event


def capture_exception(exception: Exception, **kwargs) -> Optional[str]:
    """Capture an exception with Sentry."""
    if settings.SENTRY_DSN:
        return sentry_sdk.capture_exception(exception, **kwargs)
    else:
        logger.error(f"Exception occurred: {exception}", exc_info=True)
        return None


def capture_message(message: str, level: str = "info", **kwargs) -> Optional[str]:
    """Capture a message with Sentry."""
    if settings.SENTRY_DSN:
        return sentry_sdk.capture_message(message, level=level, **kwargs)
    else:
        getattr(logger, level.lower(), logger.info)(message)
        return None


def add_breadcrumb(message: str, category: str = "custom", level: str = "info", data: Optional[dict] = None) -> None:
    """Add a breadcrumb to Sentry."""
    if settings.SENTRY_DSN:
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data or {}
        )


def set_user(user_id: str, email: Optional[str] = None, **kwargs) -> None:
    """Set user context for Sentry."""
    if settings.SENTRY_DSN:
        sentry_sdk.set_user({
            "id": user_id,
            "email": email,
            **kwargs
        })


def set_tag(key: str, value: str) -> None:
    """Set a tag for Sentry events."""
    if settings.SENTRY_DSN:
        sentry_sdk.set_tag(key, value)


def set_context(key: str, context: dict) -> None:
    """Set additional context for Sentry events."""
    if settings.SENTRY_DSN:
        sentry_sdk.set_context(key, context)


class MetricsCollector:
    """Simple metrics collector for application metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.counters = {}
        self.gauges = {}

    def increment_counter(self, name: str, value: int = 1, tags: Optional[dict] = None) -> None:
        """Increment a counter metric."""
        key = f"{name}:{tags}" if tags else name
        self.counters[key] = self.counters.get(key, 0) + value

    def set_gauge(self, name: str, value: float, tags: Optional[dict] = None) -> None:
        """Set a gauge metric."""
        key = f"{name}:{tags}" if tags else name
        self.gauges[key] = value

    def get_metrics(self) -> dict:
        """Get all collected metrics."""
        return {
            "counters": self.counters,
            "gauges": self.gauges,
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.counters.clear()
        self.gauges.clear()


# Global metrics collector instance
metrics = MetricsCollector()