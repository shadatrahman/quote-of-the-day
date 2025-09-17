"""
Integration test fixtures and configuration.
"""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.core.database import db_manager
from src.core.config import settings


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for integration tests."""
    # Create a test database engine
    test_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    # Create session factory
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Start a transaction
        async with session.begin():
            yield session
            # Transaction will be rolled back automatically
            await session.rollback()

    await test_engine.dispose()


@pytest.fixture(scope="function")
async def clean_db():
    """Ensure clean database state for each test."""
    # Create a test database engine
    test_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    # Create session factory
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Start a transaction
        async with session.begin():
            # Clean up any existing test data
            await session.execute(
                "DELETE FROM users WHERE email LIKE 'test%@example.com'"
            )
            await session.commit()
            yield session
            # Clean up after test
            await session.execute(
                "DELETE FROM users WHERE email LIKE 'test%@example.com'"
            )
            await session.commit()
            # Transaction will be rolled back automatically
            await session.rollback()

    await test_engine.dispose()


@pytest.fixture(scope="function")
async def test_session():
    """Create a test database session for direct use."""
    # Create a test database engine
    test_engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    # Create session factory
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    # Create session
    session = async_session()

    # Start a transaction
    await session.begin()

    # Clean up any existing test data
    await session.execute("DELETE FROM users WHERE email LIKE 'test%@example.com'")
    await session.commit()

    yield session

    # Clean up after test
    await session.execute("DELETE FROM users WHERE email LIKE 'test%@example.com'")
    await session.commit()

    # Close session and dispose engine
    await session.close()
    await test_engine.dispose()
