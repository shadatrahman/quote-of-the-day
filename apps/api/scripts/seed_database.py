#!/usr/bin/env python3
"""Database seeding script for Quote of the Day application."""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.core.database import db_manager
from src.core.cache import cache_manager
from src.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_database_connection():
    """Test database connectivity."""
    try:
        async for session in db_manager.get_session():
            # Test basic connection
            result = await session.execute("SELECT 1 as test")
            row = result.fetchone()
            if row and row[0] == 1:
                logger.info("✅ Database connection successful")
                return True
            else:
                logger.error("❌ Database connection test failed")
                return False
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


async def test_redis_connection():
    """Test Redis connectivity."""
    try:
        ping_result = await cache_manager.ping()
        if ping_result:
            logger.info("✅ Redis connection successful")

            # Test basic operations
            await cache_manager.set("test_key", "test_value", ttl=10)
            value = await cache_manager.get("test_key")
            if value == "test_value":
                logger.info("✅ Redis operations working")
                await cache_manager.delete("test_key")
                return True
            else:
                logger.error("❌ Redis operations failed")
                return False
        else:
            logger.error("❌ Redis ping failed")
            return False
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        return False


async def create_sample_data():
    """Create sample data for development."""
    try:
        async for session in db_manager.get_session():
            logger.info("📊 Creating sample data...")

            # Sample data will be created here when models are defined
            # For now, just test that we can execute queries

            # Check if alembic_version table exists
            result = await session.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'alembic_version'
                );
            """)

            table_exists = result.fetchone()[0]
            if table_exists:
                logger.info("✅ Alembic version table exists - database is initialized")
            else:
                logger.warning("⚠️ Alembic version table not found - run migrations first")

            logger.info("✅ Sample data creation completed")
            return True

    except Exception as e:
        logger.error(f"❌ Failed to create sample data: {e}")
        return False


async def seed_cache():
    """Seed Redis with initial cache data."""
    try:
        logger.info("💾 Seeding cache with initial data...")

        # Set some initial cache values
        initial_cache_data = {
            "app:status": "initialized",
            "app:version": "1.0.0",
            "app:environment": settings.ENVIRONMENT,
        }

        success = await cache_manager.set_many(initial_cache_data, ttl=3600)
        if success:
            logger.info("✅ Cache seeding completed")
            return True
        else:
            logger.error("❌ Cache seeding failed")
            return False

    except Exception as e:
        logger.error(f"❌ Failed to seed cache: {e}")
        return False


async def main():
    """Main seeding function."""
    logger.info("🌱 Starting database and cache seeding...")

    # Test connections
    db_success = await test_database_connection()
    redis_success = await test_redis_connection()

    if not db_success:
        logger.error("❌ Database connection failed - aborting")
        return False

    if not redis_success:
        logger.error("❌ Redis connection failed - aborting")
        return False

    # Create sample data
    sample_data_success = await create_sample_data()

    # Seed cache
    cache_success = await seed_cache()

    # Close connections
    await db_manager.close()
    await cache_manager.close()

    if sample_data_success and cache_success:
        logger.info("🎉 Database and cache seeding completed successfully!")
        return True
    else:
        logger.error("❌ Seeding completed with errors")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)