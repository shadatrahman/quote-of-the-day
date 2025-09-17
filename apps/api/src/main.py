"""
FastAPI main application entry point for Quote of the Day API.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn

from src.core.config import settings
from src.core.exceptions import setup_exception_handlers
from src.core.database import db_manager
from src.core.cache import cache_manager
from src.core.logging import setup_logging, RequestLoggingMiddleware, get_logger
from src.core.monitoring import setup_sentry, metrics
from src.core.cloudwatch import setup_cloudwatch_logging
from src.api.v1.router import api_router
from src.core.stripe_config import router as stripe_router

# Setup logging and monitoring before creating the app
setup_logging()
setup_cloudwatch_logging()
setup_sentry()
logger = get_logger("quote.api.main")

# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(
        "Starting Quote of the Day API",
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        debug=settings.DEBUG,
    )
    yield
    # Shutdown
    logger.info("Shutting down Quote of the Day API")
    await db_manager.close()
    await cache_manager.close()


# Create FastAPI application instance
app = FastAPI(
    title="Quote of the Day API",
    description="Personalized Quote of the Day API with subscription tiers",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# Configure rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware for security (disabled in test environment)
if settings.ENVIRONMENT != "test":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Setup exception handlers
setup_exception_handlers(app)

# Include API routes
app.include_router(api_router, prefix="/api/v1")
app.include_router(stripe_router)

# Application startup and shutdown events are now handled by lifespan


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "checks": {"database": "unknown", "redis": "unknown"},
    }

    # Check database connection
    try:
        async for session in db_manager.get_session():
            await session.execute("SELECT 1")
            health_status["checks"]["database"] = "healthy"
            break
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Check Redis connection
    try:
        redis_ping = await cache_manager.ping()
        health_status["checks"]["redis"] = "healthy" if redis_ping else "unhealthy"
        if not redis_ping and health_status["status"] == "healthy":
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        if health_status["status"] == "healthy":
            health_status["status"] = "degraded"

    # Determine overall status - only set to unhealthy if database is unhealthy
    if "unhealthy" in health_status["checks"]["database"]:
        health_status["status"] = "unhealthy"

    return health_status


@app.get("/metrics")
async def get_metrics():
    """Application metrics endpoint."""
    if settings.is_production:
        # In production, this might be protected or only available to monitoring systems
        return {"message": "Metrics endpoint not available in production"}

    return {
        "metrics": metrics.get_metrics(),
        "system": {
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0",
        },
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Quote of the Day API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs" if not settings.is_production else None,
    }


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
