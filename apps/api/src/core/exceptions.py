"""
Exception handlers for the FastAPI application.
"""

import logging
from typing import Union
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
import traceback
import uuid

logger = logging.getLogger(__name__)


class QuoteAPIException(Exception):
    """Base exception class for Quote API."""

    def __init__(
        self, message: str, status_code: int = 500, error_code: str = "INTERNAL_ERROR"
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class ValidationException(QuoteAPIException):
    """Exception for validation errors."""

    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, 400, "VALIDATION_ERROR")


class NotFoundError(QuoteAPIException):
    """Exception for not found errors."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404, "NOT_FOUND")


class UnauthorizedError(QuoteAPIException):
    """Exception for unauthorized access."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401, "UNAUTHORIZED")


class ForbiddenError(QuoteAPIException):
    """Exception for forbidden access."""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, 403, "FORBIDDEN")


class AuthenticationError(QuoteAPIException):
    """Exception for authentication errors."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401, "AUTHENTICATION_ERROR")


class ValidationError(QuoteAPIException):
    """Exception for validation errors."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, 400, "VALIDATION_ERROR")


class ConflictError(QuoteAPIException):
    """Exception for conflict errors."""

    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, 409, "CONFLICT")


def create_error_response(
    status_code: int,
    message: str,
    error_code: str = "UNKNOWN_ERROR",
    request_id: str = None,
    details: dict = None,
) -> dict:
    """Create standardized error response."""
    return {
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id or str(uuid.uuid4()),
            "details": details or {},
        }
    }


async def quote_api_exception_handler(request: Request, exc: QuoteAPIException):
    """Handle QuoteAPIException instances."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    logger.error(
        f"QuoteAPIException: {exc.error_code} - {exc.message}",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "error_code": exc.error_code,
            "path": str(request.url),
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            message=exc.message,
            error_code=exc.error_code,
            request_id=request_id,
        ),
    )


async def http_exception_handler(
    request: Request, exc: Union[HTTPException, StarletteHTTPException]
):
    """Handle HTTP exceptions."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "path": str(request.url),
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            status_code=exc.status_code,
            message=str(exc.detail),
            error_code="HTTP_ERROR",
            request_id=request_id,
        ),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"])
        errors.append({"field": field, "message": error["msg"], "type": error["type"]})

    logger.warning(
        f"Validation Error: {len(errors)} validation errors",
        extra={
            "request_id": request_id,
            "errors": errors,
            "path": str(request.url),
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=422,
        content=create_error_response(
            status_code=422,
            message="Validation failed",
            error_code="VALIDATION_ERROR",
            request_id=request_id,
            details={"validation_errors": errors},
        ),
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    logger.error(
        f"Unhandled Exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "request_id": request_id,
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc(),
            "path": str(request.url),
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=500,
        content=create_error_response(
            status_code=500,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            request_id=request_id,
        ),
    )


def setup_exception_handlers(app: FastAPI):
    """Setup all exception handlers for the FastAPI app."""
    app.add_exception_handler(QuoteAPIException, quote_api_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
