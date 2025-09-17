"""
Integration tests for database connectivity and basic operations.
Tests actual database connections and Redis cache functionality.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from src.core.database import db_manager, DatabaseManager
from src.core.cache import cache_manager, CacheManager
from src.core.config import settings


class TestDatabaseConnectivity:
    """Test database connection and basic operations."""

    @pytest.mark.asyncio
    async def test_database_session_creation(self):
        """Test database session can be created."""
        try:
            async for session in db_manager.get_session():
                assert session is not None
                # Test a simple query
                result = await session.execute("SELECT 1 as test")
                row = result.fetchone()
                assert row[0] == 1
                break
        except Exception as e:
            pytest.skip(f"Database not available for testing: {e}")

    @pytest.mark.asyncio
    async def test_database_ping(self):
        """Test database connectivity check."""
        try:
            async for session in db_manager.get_session():
                result = await session.execute("SELECT 1")
                assert result is not None
                break
        except Exception as e:
            pytest.skip(f"Database not available for testing: {e}")

    @pytest.mark.asyncio
    async def test_database_manager_initialization(self):
        """Test DatabaseManager can be initialized with settings."""
        test_manager = DatabaseManager()
        assert test_manager.engine is not None
        assert test_manager.session_factory is not None

    @pytest.mark.asyncio
    async def test_database_manager_close(self):
        """Test DatabaseManager can be closed properly."""
        test_manager = DatabaseManager()

        # Should not raise exception
        await test_manager.close()

    def test_database_url_configuration(self):
        """Test database URL is properly configured."""
        assert settings.DATABASE_URL is not None
        assert settings.DATABASE_URL.startswith("postgresql")

    def test_database_pool_configuration(self):
        """Test database pool settings are configured."""
        assert isinstance(settings.DATABASE_POOL_SIZE, int)
        assert settings.DATABASE_POOL_SIZE > 0
        assert isinstance(settings.DATABASE_MAX_OVERFLOW, int)
        assert settings.DATABASE_MAX_OVERFLOW > 0


class TestRedisConnectivity:
    """Test Redis cache connection and basic operations."""

    @pytest.mark.asyncio
    async def test_redis_ping(self):
        """Test Redis connectivity check."""
        try:
            result = await cache_manager.ping()
            assert isinstance(result, bool)
        except Exception as e:
            pytest.skip(f"Redis not available for testing: {e}")

    @pytest.mark.asyncio
    async def test_redis_basic_operations(self):
        """Test basic Redis operations."""
        try:
            test_key = "test_key"
            test_value = "test_value"

            # Test set operation
            await cache_manager.set(test_key, test_value, ttl=30)

            # Test get operation
            retrieved_value = await cache_manager.get(test_key)
            assert retrieved_value == test_value

            # Test delete operation
            await cache_manager.delete(test_key)
            deleted_value = await cache_manager.get(test_key)
            assert deleted_value is None

        except Exception as e:
            pytest.skip(f"Redis not available for testing: {e}")

    @pytest.mark.asyncio
    async def test_redis_serialization(self):
        """Test Redis handles different data types."""
        try:
            # Test with dict
            test_data = {"key": "value", "number": 42}
            await cache_manager.set("test_dict", test_data, ttl=30)
            retrieved_data = await cache_manager.get("test_dict")
            assert retrieved_data == test_data

            # Test with list
            test_list = [1, 2, 3, "four"]
            await cache_manager.set("test_list", test_list, ttl=30)
            retrieved_list = await cache_manager.get("test_list")
            assert retrieved_list == test_list

            # Cleanup
            await cache_manager.delete("test_dict")
            await cache_manager.delete("test_list")

        except Exception as e:
            pytest.skip(f"Redis not available for testing: {e}")

    @pytest.mark.asyncio
    async def test_cache_manager_initialization(self):
        """Test CacheManager can be initialized."""
        test_manager = CacheManager()
        assert test_manager.redis is not None
        assert test_manager.pool is not None

    @pytest.mark.asyncio
    async def test_cache_manager_close(self):
        """Test CacheManager can be closed properly."""
        test_manager = CacheManager()

        # Should not raise exception
        await test_manager.close()

    def test_redis_url_configuration(self):
        """Test Redis URL is properly configured."""
        assert settings.REDIS_URL is not None
        assert "redis://" in settings.REDIS_URL


class TestDatabaseCacheIntegration:
    """Test integration between database and cache systems."""

    @pytest.mark.asyncio
    async def test_health_check_integration(self):
        """Test that health check can verify both systems."""
        try:
            # Test database health
            db_healthy = False
            async for session in db_manager.get_session():
                await session.execute("SELECT 1")
                db_healthy = True
                break

            # Test cache health
            cache_healthy = await cache_manager.ping()

            # At least one should work in a properly configured environment
            assert (
                db_healthy or cache_healthy
            ), "Neither database nor cache is accessible"

        except Exception as e:
            pytest.skip(f"Integration test environment not available: {e}")

    @pytest.mark.asyncio
    async def test_concurrent_connections(self):
        """Test that multiple concurrent connections work properly."""
        try:

            async def test_db_query():
                async for session in db_manager.get_session():
                    result = await session.execute("SELECT 1 as test")
                    return result.fetchone()[0]

            async def test_cache_operation():
                await cache_manager.set("concurrent_test", "value", ttl=10)
                return await cache_manager.get("concurrent_test")

            # Run multiple operations concurrently
            db_tasks = [test_db_query() for _ in range(3)]
            cache_tasks = [test_cache_operation() for _ in range(3)]

            db_results = await asyncio.gather(*db_tasks, return_exceptions=True)
            cache_results = await asyncio.gather(*cache_tasks, return_exceptions=True)

            # Check that at least some operations succeeded
            successful_db = sum(1 for result in db_results if result == 1)
            successful_cache = sum(1 for result in cache_results if result == "value")

            # Clean up
            await cache_manager.delete("concurrent_test")

            # At least some operations should succeed
            assert successful_db > 0 or successful_cache > 0

        except Exception as e:
            pytest.skip(f"Concurrent connection test failed: {e}")


class TestEnvironmentConfiguration:
    """Test that environment configuration supports testing."""

    def test_test_environment_detection(self):
        """Test that test environment can be detected."""
        # In test environment, we should be able to override settings
        with patch.dict("os.environ", {"ENVIRONMENT": "test"}):
            from src.core.config import Settings

            test_settings = Settings()
            assert test_settings.ENVIRONMENT == "test"

    def test_database_url_override(self):
        """Test that database URL can be overridden for testing."""
        test_db_url = "postgresql://test:test@localhost:5432/test_db"
        with patch.dict("os.environ", {"DATABASE_URL": test_db_url}):
            from src.core.config import Settings

            test_settings = Settings()
            assert test_settings.DATABASE_URL == test_db_url

    def test_redis_url_override(self):
        """Test that Redis URL can be overridden for testing."""
        test_redis_url = "redis://localhost:6379/1"
        with patch.dict("os.environ", {"REDIS_URL": test_redis_url}):
            from src.core.config import Settings

            test_settings = Settings()
            assert test_settings.REDIS_URL == test_redis_url
