"""E2E testing fixtures and configuration."""
import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure async backend."""
    return "asyncio"


# Create a test database URL (using the same database but with proper test isolation)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite+aiosqlite:///./test.db"  # Default to SQLite for easy testing
)


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    from app.core.database import Base
    
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    
    # Import models to register them
    import app.models.database  # noqa: F401
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""
    from app.main import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
async def authenticated_client(client: AsyncClient, db_session: AsyncSession) -> AsyncClient:
    """Create authenticated test HTTP client."""
    from datetime import datetime, timedelta, timezone
    import jwt
    from app.models.database import User
    from app.core.config import settings
    
    # Create test user
    test_user = User(
        telegram_id=123456789,
        username="testuser",
        first_name="Test",
        last_name="User",
        language_code="en",
        xp=100,
        level=2,
        current_streak=5,
        longest_streak=10,
        total_queries=50,
        last_active_date=datetime.utcnow(),
    )
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)
    
    # Create JWT token
    payload = {
        "sub": str(test_user.telegram_id),
        "telegram_id": test_user.telegram_id,
        "username": test_user.username,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    
    # Add authorization header to client
    client.headers["Authorization"] = f"Bearer {token}"
    
    return client
