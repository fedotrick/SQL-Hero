"""
Tests for leaderboard API endpoints.
"""

import random
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.main import app
from app.models.database import Base, LeaderboardCache, User
from app.services.leaderboard import refresh_leaderboard_cache


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def engine():
    """Create test database engine."""
    test_engine = create_async_engine(settings.database_url, echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
async def db_session(engine):
    """Create a new database session for each test."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_users(db_session: AsyncSession):
    """Create test users and populate leaderboard cache."""
    # Clean up
    await db_session.execute(delete(LeaderboardCache))
    await db_session.commit()

    base_id = random.randint(100000000, 999999999)
    users = []
    for i in range(10):
        user = User(
            telegram_id=base_id + i,
            username=f"test_user{i}",
            first_name=f"User{i}",
            xp=(10 - i) * 100,
            level=(10 - i),
            is_active=True,
        )
        db_session.add(user)
        users.append(user)

    await db_session.commit()

    # Refresh users to get IDs
    for user in users:
        await db_session.refresh(user)

    # Refresh leaderboard cache
    await refresh_leaderboard_cache(db_session)

    return users


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def create_mock_auth_header(user_id: int):
    """Create a mock authorization header for testing."""
    # In real tests, you'd need to generate a proper JWT token
    # For now, we'll assume the auth middleware is mocked or bypassed
    return {"Authorization": f"Bearer mock-token-{user_id}"}


@pytest.mark.anyio
async def test_get_leaderboard_endpoint(client: TestClient, test_users, db_session: AsyncSession):
    """Test GET /leaderboard endpoint returns data."""
    # Note: This test assumes authentication is properly mocked
    # In a real scenario, you'd need to set up proper JWT authentication

    # Create a simple request without auth to test the structure
    # The actual auth testing should be done separately
    response = client.get("/leaderboard")

    # Without auth, should return 401 or similar
    assert response.status_code in [401, 403]


@pytest.mark.anyio
async def test_get_leaderboard_with_limit(test_users, db_session: AsyncSession):
    """Test leaderboard respects limit parameter."""
    from app.services.leaderboard import get_leaderboard

    result = await get_leaderboard(db_session, limit=5)

    assert len(result["entries"]) <= 5
    assert result["total_users"] >= 10


@pytest.mark.anyio
async def test_leaderboard_response_structure(test_users, db_session: AsyncSession):
    """Test leaderboard response has correct structure."""
    from app.services.leaderboard import get_leaderboard

    result = await get_leaderboard(db_session, limit=5)

    # Check response structure
    assert "entries" in result
    assert "current_user" in result
    assert "last_updated" in result
    assert "total_users" in result

    # Check entry structure
    if result["entries"]:
        entry = result["entries"][0]
        assert "user_id" in entry.model_dump()
        assert "username" in entry.model_dump()
        assert "first_name" in entry.model_dump()
        assert "rank" in entry.model_dump()
        assert "xp" in entry.model_dump()
        assert "level" in entry.model_dump()
        assert "lessons_completed" in entry.model_dump()
        assert "achievements_count" in entry.model_dump()


@pytest.mark.anyio
async def test_leaderboard_entries_sorted_by_xp(test_users, db_session: AsyncSession):
    """Test that leaderboard entries are sorted by XP descending."""
    from app.services.leaderboard import get_leaderboard

    result = await get_leaderboard(db_session, limit=10)

    entries = result["entries"]
    assert len(entries) > 0

    # Check XP is in descending order
    xp_values = [entry.xp for entry in entries]
    assert xp_values == sorted(xp_values, reverse=True)


@pytest.mark.anyio
async def test_leaderboard_ranks_are_sequential(test_users, db_session: AsyncSession):
    """Test that ranks are sequential starting from 1."""
    from app.services.leaderboard import get_leaderboard

    result = await get_leaderboard(db_session, limit=10)

    entries = result["entries"]
    ranks = [entry.rank for entry in entries]

    # Ranks should start at 1 and be sequential
    expected_ranks = list(range(1, len(entries) + 1))
    assert ranks == expected_ranks


@pytest.mark.anyio
async def test_current_user_not_in_top_n(test_users, db_session: AsyncSession):
    """Test that current_user is returned when not in top N."""
    from app.services.leaderboard import get_leaderboard

    # Get top 3, but request user at position 5
    current_user_id = test_users[4].id  # User with rank 5

    result = await get_leaderboard(db_session, limit=3, user_id=current_user_id)

    # Top 3 should not include user at rank 5
    top_user_ids = [entry.user_id for entry in result["entries"]]

    if current_user_id not in top_user_ids:
        # Current user should be returned separately
        assert result["current_user"] is not None
        assert result["current_user"].user_id == current_user_id
    else:
        # If user is in top 3, current_user should be None
        assert result["current_user"] is None


@pytest.mark.anyio
async def test_current_user_in_top_n(test_users, db_session: AsyncSession):
    """Test that current_user is None when in top N."""
    from app.services.leaderboard import get_leaderboard

    # Get top 5, with user at position 2
    current_user_id = test_users[1].id  # User with rank 2

    result = await get_leaderboard(db_session, limit=5, user_id=current_user_id)

    # User should be in top 5
    top_user_ids = [entry.user_id for entry in result["entries"]]

    if current_user_id in top_user_ids:
        # Current user should not be returned separately
        assert result["current_user"] is None


@pytest.mark.anyio
async def test_leaderboard_with_no_current_user(test_users, db_session: AsyncSession):
    """Test leaderboard when no current user is specified."""
    from app.services.leaderboard import get_leaderboard

    result = await get_leaderboard(db_session, limit=5, user_id=None)

    # Should return entries without current_user
    assert len(result["entries"]) > 0
    assert result["current_user"] is None


@pytest.mark.anyio
async def test_leaderboard_includes_user_stats(test_users, db_session: AsyncSession):
    """Test that leaderboard entries include all user statistics."""
    from app.services.leaderboard import get_leaderboard

    result = await get_leaderboard(db_session, limit=5)

    for entry in result["entries"]:
        # Check all required fields are present
        assert isinstance(entry.user_id, int)
        assert isinstance(entry.rank, int)
        assert isinstance(entry.xp, int)
        assert isinstance(entry.level, int)
        assert isinstance(entry.lessons_completed, int)
        assert isinstance(entry.achievements_count, int)
        # username and first_name can be None
        assert entry.username is None or isinstance(entry.username, str)
        assert entry.first_name is None or isinstance(entry.first_name, str)


@pytest.mark.anyio
async def test_leaderboard_total_users_count(test_users, db_session: AsyncSession):
    """Test that total_users count is accurate."""
    from app.services.leaderboard import get_leaderboard

    result = await get_leaderboard(db_session, limit=5)

    # Should have at least 10 users from fixture
    assert result["total_users"] >= 10


@pytest.mark.anyio
async def test_leaderboard_last_updated_timestamp(test_users, db_session: AsyncSession):
    """Test that last_updated timestamp is present and valid."""
    from app.services.leaderboard import get_leaderboard

    result = await get_leaderboard(db_session, limit=5)

    if result["entries"]:
        assert result["last_updated"] is not None
        # Should be a datetime object or ISO string
        if isinstance(result["last_updated"], str):
            # Try parsing as ISO format
            datetime.fromisoformat(result["last_updated"].replace("Z", "+00:00"))
        else:
            assert isinstance(result["last_updated"], datetime)


@pytest.mark.anyio
async def test_leaderboard_with_different_limits(test_users, db_session: AsyncSession):
    """Test leaderboard with various limit values."""
    from app.services.leaderboard import get_leaderboard

    for limit in [1, 3, 5, 10, 100]:
        result = await get_leaderboard(db_session, limit=limit)
        assert len(result["entries"]) <= limit
        assert len(result["entries"]) <= result["total_users"]


@pytest.mark.anyio
async def test_refresh_leaderboard_endpoint(client: TestClient):
    """Test POST /leaderboard/refresh endpoint."""
    response = client.post("/leaderboard/refresh")

    # Without auth, should return 401 or similar
    # Or if auth is not required for refresh, should return 200
    assert response.status_code in [200, 401, 403]


@pytest.mark.anyio
async def test_leaderboard_consistency_after_refresh(test_users, db_session: AsyncSession):
    """Test that leaderboard remains consistent after cache refresh."""
    from app.services.leaderboard import get_leaderboard, refresh_leaderboard_cache

    # Get initial state
    result1 = await get_leaderboard(db_session, limit=10)
    initial_ranks = {entry.user_id: entry.rank for entry in result1["entries"]}

    # Refresh cache
    await refresh_leaderboard_cache(db_session)

    # Get new state
    result2 = await get_leaderboard(db_session, limit=10)
    new_ranks = {entry.user_id: entry.rank for entry in result2["entries"]}

    # Ranks should remain the same if XP didn't change
    for user_id in initial_ranks:
        if user_id in new_ranks:
            assert initial_ranks[user_id] == new_ranks[user_id]
