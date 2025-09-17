"""
Unit tests for the FastAPI main application module.
Tests basic functionality of core endpoints without external dependencies.
"""

import pytest
from unittest.mock import AsyncMock, patch, PropertyMock, MagicMock
from fastapi.testclient import TestClient
from src.main import app


class TestMainApplication:
    """Test class for main FastAPI application."""

    def setup_method(self):
        """Setup test client."""
        # Create a test app without TrustedHostMiddleware
        from fastapi import FastAPI
        from src.main import app

        # Create a test app that's identical to the main app but without TrustedHostMiddleware
        test_app = FastAPI(
            title="Quote of the Day API Test",
            description="Test version without TrustedHostMiddleware",
            version="1.0.0",
        )

        # Copy all routes from the main app
        for route in app.routes:
            test_app.routes.append(route)

        # Copy middleware (except TrustedHostMiddleware)
        for middleware in app.user_middleware:
            if middleware.cls.__name__ != "TrustedHostMiddleware":
                test_app.add_middleware(middleware.cls, **middleware.kwargs)

        self.client = TestClient(test_app)

    def test_root_endpoint(self):
        """Test root endpoint returns correct response."""
        response = self.client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["message"] == "Quote of the Day API"
        assert data["version"] == "1.0.0"
        assert "environment" in data

    def test_root_endpoint_production_no_docs(self):
        """Test root endpoint in production doesn't expose docs URL."""
        with patch("src.core.config.settings.ENVIRONMENT", "production"):
            response = self.client.get("/")
            assert response.status_code == 200

            data = response.json()
            assert data["docs_url"] is None

    def test_root_endpoint_development_has_docs(self):
        """Test root endpoint in development exposes docs URL."""
        with patch("src.core.config.settings.ENVIRONMENT", "development"):
            response = self.client.get("/")
            assert response.status_code == 200

            data = response.json()
            assert data["docs_url"] == "/docs"

    def test_metrics_endpoint_development(self):
        """Test metrics endpoint in development mode."""
        with patch("src.core.config.settings.ENVIRONMENT", "development"):
            with patch("src.main.metrics.get_metrics") as mock_metrics:
                mock_metrics.return_value = {"test_metric": 1.0}

                response = self.client.get("/metrics")
                assert response.status_code == 200

                data = response.json()
                assert "metrics" in data
                assert "system" in data
                assert data["system"]["version"] == "1.0.0"

    def test_metrics_endpoint_production(self):
        """Test metrics endpoint in production mode."""
        with patch("src.core.config.settings.ENVIRONMENT", "production"):
            response = self.client.get("/metrics")
            assert response.status_code == 200

            data = response.json()
            assert data["message"] == "Metrics endpoint not available in production"

    @pytest.mark.asyncio
    async def test_health_endpoint_all_healthy(self):
        """Test health endpoint when all services are healthy."""
        with patch("src.main.db_manager.get_session") as mock_db:
            with patch("src.main.cache_manager.ping") as mock_redis:
                # Mock database session
                mock_session = AsyncMock()
                mock_session.execute = AsyncMock()

                # Create a proper async iterator for the session
                async def async_session_generator():
                    yield mock_session

                mock_db.return_value = async_session_generator()

                # Mock Redis ping
                mock_redis.return_value = True

                response = self.client.get("/health")
                assert response.status_code == 200

                data = response.json()
                assert data["status"] == "healthy"
                assert data["version"] == "1.0.0"
                assert data["checks"]["database"] == "healthy"
                assert data["checks"]["redis"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_endpoint_database_unhealthy(self):
        """Test health endpoint when database is unhealthy."""
        with patch("src.main.db_manager.get_session") as mock_db:
            with patch("src.main.cache_manager.ping") as mock_redis:
                # Mock database failure
                mock_db.side_effect = Exception("Database connection failed")

                # Mock Redis as healthy
                mock_redis.return_value = True

                response = self.client.get("/health")
                assert response.status_code == 200

                data = response.json()
                assert data["status"] == "unhealthy"
                assert (
                    "unhealthy: Database connection failed"
                    in data["checks"]["database"]
                )
                assert data["checks"]["redis"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_endpoint_redis_unhealthy(self):
        """Test health endpoint when Redis is unhealthy."""
        with patch("src.main.db_manager.get_session") as mock_db:
            with patch("src.main.cache_manager.ping") as mock_redis:
                # Mock database as healthy
                mock_session = AsyncMock()
                mock_session.execute = AsyncMock()

                # Create a proper async iterator for the session
                async def async_session_generator():
                    yield mock_session

                mock_db.return_value = async_session_generator()

                # Mock Redis failure
                mock_redis.side_effect = Exception("Redis connection failed")

                response = self.client.get("/health")
                assert response.status_code == 200

                data = response.json()
                assert data["status"] == "degraded"
                assert data["checks"]["database"] == "healthy"
                assert "unhealthy: Redis connection failed" in data["checks"]["redis"]

    @pytest.mark.asyncio
    async def test_health_endpoint_degraded_status(self):
        """Test health endpoint returns degraded status when Redis is down but database is up."""
        with patch("src.main.db_manager.get_session") as mock_db:
            with patch("src.main.cache_manager.ping") as mock_redis:
                # Mock database as healthy
                mock_session = AsyncMock()
                mock_session.execute = AsyncMock()

                # Create a proper async iterator for the session
                async def async_session_generator():
                    yield mock_session

                mock_db.return_value = async_session_generator()

                # Mock Redis as unhealthy but not throwing exception
                mock_redis.return_value = False

                response = self.client.get("/health")
                assert response.status_code == 200

                data = response.json()
                assert data["status"] == "degraded"
                assert data["checks"]["database"] == "healthy"
                assert data["checks"]["redis"] == "unhealthy"


class TestApplicationLifecycle:
    """Test application startup and shutdown events."""

    @pytest.mark.asyncio
    async def test_lifespan_startup(self):
        """Test lifespan startup logging."""
        with patch("src.main.logger.info") as mock_logger:
            from src.main import lifespan

            async with lifespan(app):
                pass
            # Should have been called during startup
            assert mock_logger.call_count >= 1

    @pytest.mark.asyncio
    async def test_lifespan_shutdown(self):
        """Test lifespan shutdown closes connections."""
        with patch("src.main.db_manager.close") as mock_db_close:
            with patch("src.main.cache_manager.close") as mock_cache_close:
                with patch("src.main.logger.info") as mock_logger:
                    from src.main import lifespan

                    async with lifespan(app):
                        pass
                    # Should have been called during shutdown
                    mock_db_close.assert_called_once()
                    mock_cache_close.assert_called_once()


class TestAppConfiguration:
    """Test FastAPI application configuration."""

    def test_app_metadata(self):
        """Test FastAPI application metadata."""
        assert app.title == "Quote of the Day API"
        assert (
            app.description
            == "Personalized Quote of the Day API with subscription tiers"
        )
        assert app.version == "1.0.0"

    def test_middleware_configuration(self):
        """Test that middleware is properly configured."""
        # Check that middlewares are added (we can't easily test their config without diving deep)
        middleware_classes = [
            middleware.cls.__name__ for middleware in app.user_middleware
        ]

        # Should include our custom and third-party middleware
        assert "CORSMiddleware" in middleware_classes
        assert "TrustedHostMiddleware" in middleware_classes
        assert "RequestLoggingMiddleware" in middleware_classes
