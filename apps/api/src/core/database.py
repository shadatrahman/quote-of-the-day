"""Database configuration and session management."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool, QueuePool

from src.core.config import settings


class DatabaseManager:
    """Database connection and session management."""

    def __init__(self):
        """Initialize database manager."""
        # Create async engine
        engine_kwargs = {
            "url": settings.DATABASE_URL,
            "echo": settings.DEBUG,
            "pool_pre_ping": True,
            "pool_recycle": 3600,  # Recycle connections after 1 hour
        }

        if settings.is_production:
            engine_kwargs.update(
                {
                    "poolclass": QueuePool,
                    "pool_size": settings.DATABASE_POOL_SIZE,
                    "max_overflow": settings.DATABASE_MAX_OVERFLOW,
                }
            )
        else:
            engine_kwargs["poolclass"] = NullPool

        self.engine = create_async_engine(**engine_kwargs)

        # Create session factory
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session."""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def close(self):
        """Close database engine."""
        await self.engine.dispose()


# Create global database manager instance
db_manager = DatabaseManager()


# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async for session in db_manager.get_session():
        yield session
