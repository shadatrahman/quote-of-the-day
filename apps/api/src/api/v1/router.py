"""
Main API router for version 1.
"""

from fastapi import APIRouter

from src.api.v1.auth import router as auth_router

# Create the main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth_router)


@api_router.get("/")
async def api_root():
    """API root endpoint."""
    return {"message": "Quote of the Day API v1", "version": "1.0.0"}


@api_router.get("/health")
async def health_check():
    """Health check endpoint for API v1."""
    return {"status": "healthy", "api_version": "1.0.0", "service": "quote-api"}
