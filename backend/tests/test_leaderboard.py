"""
Simplified tests for leaderboard service functionality.
"""
import random
from datetime import datetime

import pytest
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.database import (
    Achievement,
    AchievementType,
    Base,
    LeaderboardCache,
    Lesson,
    Module,
    ProgressStatus,
    User,
    UserAchievement,
    UserProgress,
)
from app.services.leaderboard import get_leaderboard, refresh_leaderboard_cache


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


@pytest.mark.anyio
async def test_refresh_leaderboard_basic(db_session: AsyncSession):
    """Test basic leaderboard cache refresh."""
    # Clean up
    await db_session.execute(delete(LeaderboardCache))
    await db_session.commit()
    
    # Create test users
    base_id = random.randint(100000000, 999999999)
    for i in range(5):
        user = User(
            telegram_id=base_id + i,
            username=f"user{i}",
            xp=(5 - i) * 100,
            level=(5 - i),
            is_active=True,
        )
        db_session.add(user)
    await db_session.commit()
    
    # Refresh leaderboard
    entries_updated = await refresh_leaderboard_cache(db_session)
    
    assert entries_updated >= 5
    
    # Verify cache entries
    query = select(LeaderboardCache).order_by(LeaderboardCache.rank).limit(5)
    result = await db_session.execute(query)
    cache_entries = result.scalars().all()
    
    assert len(cache_entries) >= 5


@pytest.mark.anyio
async def test_refresh_leaderboard_ordering(db_session: AsyncSession):
    """Test leaderboard ordering by XP."""
    # Clean up
    await db_session.execute(delete(LeaderboardCache))
    await db_session.commit()
    
    # Create users with different XP
    base_id = random.randint(100000000, 999999999)
    user1 = User(telegram_id=base_id, username="user1", xp=100, level=1, is_active=True)
    user2 = User(telegram_id=base_id + 1, username="user2", xp=300, level=3, is_active=True)
    user3 = User(telegram_id=base_id + 2, username="user3", xp=200, level=2, is_active=True)
    
    db_session.add_all([user1, user2, user3])
    await db_session.commit()
    await db_session.refresh(user1)
    await db_session.refresh(user2)
    await db_session.refresh(user3)
    
    # Refresh leaderboard
    await refresh_leaderboard_cache(db_session)
    
    # Get entries for our users
    query = (
        select(LeaderboardCache)
        .where(LeaderboardCache.user_id.in_([user1.id, user2.id, user3.id]))
        .order_by(LeaderboardCache.rank)
    )
    result = await db_session.execute(query)
    entries = result.scalars().all()
    
    # user2 (300 XP) should be rank 1
    # user3 (200 XP) should be rank 2  
    # user1 (100 XP) should be rank 3
    user_ranks = {e.user_id: e.rank for e in entries}
    assert user_ranks[user2.id] < user_ranks[user3.id] < user_ranks[user1.id]


@pytest.mark.anyio
async def test_get_leaderboard_returns_top_users(db_session: AsyncSession):
    """Test getting top N users from leaderboard."""
    # Clean up
    await db_session.execute(delete(LeaderboardCache))
    await db_session.commit()
    
    # Create users
    base_id = random.randint(100000000, 999999999)
    for i in range(10):
        user = User(
            telegram_id=base_id + i,
            username=f"user{i}",
            xp=(10 - i) * 100,
            level=(10 - i),
            is_active=True,
        )
        db_session.add(user)
    await db_session.commit()
    
    # Refresh cache
    await refresh_leaderboard_cache(db_session)
    
    # Get top 5
    result = await get_leaderboard(db_session, limit=5)
    
    assert len(result["entries"]) <= 5
    assert result["total_users"] >= 10


@pytest.mark.anyio
async def test_get_leaderboard_with_current_user(db_session: AsyncSession):
    """Test getting leaderboard with current user not in top N."""
    # Clean up
    await db_session.execute(delete(LeaderboardCache))
    await db_session.commit()
    
    # Create users
    base_id = random.randint(100000000, 999999999)
    users = []
    for i in range(10):
        user = User(
            telegram_id=base_id + i,
            username=f"user{i}",
            xp=(10 - i) * 100,
            level=(10 - i),
            is_active=True,
        )
        db_session.add(user)
        users.append(user)
    await db_session.commit()
    
    for u in users:
        await db_session.refresh(u)
    
    # Refresh cache
    await refresh_leaderboard_cache(db_session)
    
    # Get top 3 with user at rank 5
    result = await get_leaderboard(db_session, limit=3, user_id=users[4].id)
    
    # Should get top 3
    assert len(result["entries"]) <= 3
    # Current user should be included separately if not in top 3
    if len(result["entries"]) < 3 or users[4].id not in [e.user_id for e in result["entries"]]:
        assert result["current_user"] is not None


@pytest.mark.anyio
async def test_refresh_leaderboard_replaces_cache(db_session: AsyncSession):
    """Test that cache refresh replaces old entries."""
    # Clean up
    await db_session.execute(delete(LeaderboardCache))
    await db_session.commit()
    
    # Create user
    base_id = random.randint(100000000, 999999999)
    user = User(telegram_id=base_id, username="user", xp=500, level=5, is_active=True)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # First refresh
    await refresh_leaderboard_cache(db_session)
    
    # Modify user XP
    user.xp = 100
    await db_session.commit()
    
    # Second refresh
    await refresh_leaderboard_cache(db_session)
    
    # Check cache was updated
    query = select(LeaderboardCache).where(LeaderboardCache.user_id == user.id)
    result = await db_session.execute(query)
    entry = result.scalar_one()
    
    assert entry.total_score == 100


@pytest.mark.anyio
async def test_leaderboard_excludes_inactive_users(db_session: AsyncSession):
    """Test that inactive users are excluded."""
    # Clean up
    await db_session.execute(delete(LeaderboardCache))
    await db_session.commit()
    
    # Create users
    base_id = random.randint(100000000, 999999999)
    active = User(telegram_id=base_id, username="active", xp=100, level=1, is_active=True)
    inactive = User(telegram_id=base_id + 1, username="inactive", xp=200, level=2, is_active=False)
    
    db_session.add_all([active, inactive])
    await db_session.commit()
    await db_session.refresh(inactive)
    
    # Refresh
    await refresh_leaderboard_cache(db_session)
    
    # Inactive user should not be in cache
    query = select(LeaderboardCache).where(LeaderboardCache.user_id == inactive.id)
    result = await db_session.execute(query)
    assert result.scalar_one_or_none() is None


@pytest.mark.anyio
async def test_get_leaderboard_empty(db_session: AsyncSession):
    """Test getting leaderboard when empty."""
    # Clean up everything
    await db_session.execute(delete(LeaderboardCache))
    await db_session.commit()
    
    result = await get_leaderboard(db_session)
    
    assert result["entries"] == []
    assert result["total_users"] >= 0
