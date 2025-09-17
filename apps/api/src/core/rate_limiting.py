"""Rate limiting implementation for API endpoints."""

import time
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import asyncio
from functools import wraps

from src.core.cache import cache_manager
from src.core.config import settings


class RateLimiter:
    """Rate limiter using Redis for distributed rate limiting."""

    def __init__(self, requests_per_minute: int = 5, window_minutes: int = 1):
        """Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests allowed per minute
            window_minutes: Time window in minutes for rate limiting
        """
        self.requests_per_minute = requests_per_minute
        self.window_seconds = window_minutes * 60

    async def is_allowed(self, key: str) -> bool:
        """Check if request is allowed based on rate limit.

        Args:
            key: Unique identifier for rate limiting (e.g., IP address, user ID)

        Returns:
            True if request is allowed, False otherwise
        """
        current_time = int(time.time())
        window_start = current_time - self.window_seconds

        # Get current request count for this key
        cache_key = f"rate_limit:{key}"
        request_times = await cache_manager.get(cache_key, default=[])

        # Filter out requests outside the window
        request_times = [t for t in request_times if t > window_start]

        # Check if we're under the limit
        if len(request_times) >= self.requests_per_minute:
            return False

        # Add current request time
        request_times.append(current_time)

        # Store updated request times
        await cache_manager.set(cache_key, request_times, ttl=self.window_seconds)

        return True

    async def get_remaining_requests(self, key: str) -> int:
        """Get remaining requests for the current window.

        Args:
            key: Unique identifier for rate limiting

        Returns:
            Number of remaining requests
        """
        current_time = int(time.time())
        window_start = current_time - self.window_seconds

        cache_key = f"rate_limit:{key}"
        request_times = await cache_manager.get(cache_key, default=[])

        # Filter out requests outside the window
        request_times = [t for t in request_times if t > window_start]

        return max(0, self.requests_per_minute - len(request_times))

    async def get_reset_time(self, key: str) -> int:
        """Get time when rate limit resets.

        Args:
            key: Unique identifier for rate limiting

        Returns:
            Unix timestamp when rate limit resets
        """
        current_time = int(time.time())
        window_start = current_time - self.window_seconds

        cache_key = f"rate_limit:{key}"
        request_times = await cache_manager.get(cache_key, default=[])

        if not request_times:
            return current_time

        # Find the oldest request in the current window
        oldest_request = min(request_times)
        return oldest_request + self.window_seconds


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address
    """
    # Check for forwarded headers first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fall back to direct client IP
    if hasattr(request, "client") and request.client:
        return request.client.host

    return "unknown"


def rate_limit(requests_per_minute: int = 5, window_minutes: int = 1):
    """Decorator for rate limiting endpoints.

    Args:
        requests_per_minute: Maximum requests allowed per minute
        window_minutes: Time window in minutes for rate limiting
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request object in args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                # If no request found, call function without rate limiting
                return await func(*args, **kwargs)

            # Create rate limiter
            limiter = RateLimiter(requests_per_minute, window_minutes)

            # Get client identifier
            client_ip = get_client_ip(request)
            rate_limit_key = f"auth:{client_ip}"

            # Check rate limit
            if not await limiter.is_allowed(rate_limit_key):
                remaining = await limiter.get_remaining_requests(rate_limit_key)
                reset_time = await limiter.get_reset_time(rate_limit_key)

                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests. Limit: {requests_per_minute} per {window_minutes} minute(s)",
                        "remaining": remaining,
                        "reset_time": reset_time,
                    },
                    headers={
                        "X-RateLimit-Limit": str(requests_per_minute),
                        "X-RateLimit-Remaining": str(remaining),
                        "X-RateLimit-Reset": str(reset_time),
                        "Retry-After": str(reset_time - int(time.time())),
                    },
                )

            # Call the original function
            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Pre-configured rate limiters for different endpoint types
auth_rate_limiter = RateLimiter(
    requests_per_minute=5, window_minutes=1
)  # 5 requests per minute
general_rate_limiter = RateLimiter(
    requests_per_minute=60, window_minutes=1
)  # 60 requests per minute


class RateLimitMiddleware:
    """Middleware for global rate limiting."""

    def __init__(self, app, requests_per_minute: int = 60, window_minutes: int = 1):
        """Initialize rate limiting middleware.

        Args:
            app: FastAPI application
            requests_per_minute: Maximum requests allowed per minute
            window_minutes: Time window in minutes for rate limiting
        """
        self.app = app
        self.limiter = RateLimiter(requests_per_minute, window_minutes)

    async def __call__(self, scope, receive, send):
        """Process request with rate limiting."""
        if scope["type"] == "http":
            request = Request(scope, receive)

            # Skip rate limiting for health checks and docs
            if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
                await self.app(scope, receive, send)
                return

            # Get client identifier
            client_ip = get_client_ip(request)
            rate_limit_key = f"global:{client_ip}"

            # Check rate limit
            if not await self.limiter.is_allowed(rate_limit_key):
                remaining = await self.limiter.get_remaining_requests(rate_limit_key)
                reset_time = await self.limiter.get_reset_time(rate_limit_key)

                response = JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests. Limit: {self.limiter.requests_per_minute} per {self.limiter.window_seconds // 60} minute(s)",
                        "remaining": remaining,
                        "reset_time": reset_time,
                    },
                    headers={
                        "X-RateLimit-Limit": str(self.limiter.requests_per_minute),
                        "X-RateLimit-Remaining": str(remaining),
                        "X-RateLimit-Reset": str(reset_time),
                        "Retry-After": str(reset_time - int(time.time())),
                    },
                )

                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)
