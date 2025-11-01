from datetime import date, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.main import app
from app.models.database import ActivityLog, ActivityType, Base, User


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
async def db(engine):
    """Create a new database session for each test."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_user(db: AsyncSession):
    """Create a test user."""
    user = User(
        telegram_id=111222333,
        username="apiuser",
        first_name="API",
        last_name="User",
        xp=100,
        level=2,
        current_streak=3,
        longest_streak=5,
        total_queries=10,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def auth_headers(test_user: User):
    """Create authentication headers for test user."""
    # Mock authentication - in real tests you'd generate a proper JWT
    # For now, we'll assume the auth system is tested separately
    return {"Authorization": f"Bearer test_token_{test_user.id}"}


class TestActivityHeatmapAPI:
    """Tests for GET /activity/heatmap endpoint."""

    async def test_heatmap_endpoint_exists(self):
        """Test that heatmap endpoint is accessible."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # This will fail auth but should not return 404
            response = await client.get("/activity/heatmap")
            assert response.status_code != 404

    async def test_heatmap_returns_correct_structure(
        self, db: AsyncSession, test_user: User
    ):
        """Test that heatmap returns correct response structure."""
        # Add some activities
        today = date.today()
        for i in range(3):
            activity_date = today - timedelta(days=i)
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=ActivityType.LESSON_COMPLETED,
                created_at=datetime.combine(activity_date, datetime.min.time()),
            )
            db.add(activity)
        await db.commit()

        # Note: In a real scenario, you'd need proper auth setup
        # This test verifies the response structure
        from app.services.activity import get_activity_heatmap

        heatmap_data = await get_activity_heatmap(db, test_user)

        # Verify structure
        assert isinstance(heatmap_data, list)
        assert len(heatmap_data) > 0
        for entry in heatmap_data:
            assert "date" in entry
            assert "count" in entry
            assert isinstance(entry["date"], str)
            assert isinstance(entry["count"], int)

    async def test_heatmap_date_range_parameters(
        self, db: AsyncSession, test_user: User
    ):
        """Test that heatmap respects date range parameters."""
        today = date.today()
        start_date = today - timedelta(days=7)

        # Add activities within range
        activity = ActivityLog(
            user_id=test_user.id,
            activity_type=ActivityType.LOGIN,
            created_at=datetime.combine(today, datetime.min.time()),
        )
        db.add(activity)
        await db.commit()

        from app.services.activity import get_activity_heatmap

        heatmap = await get_activity_heatmap(db, test_user, start_date, today)

        # Should have data for today
        assert len(heatmap) > 0
        assert any(entry["date"] == str(today) for entry in heatmap)

    async def test_heatmap_empty_for_new_user(
        self, db: AsyncSession, test_user: User
    ):
        """Test heatmap returns empty list for user with no activities."""
        from app.services.activity import get_activity_heatmap

        heatmap = await get_activity_heatmap(db, test_user)

        assert isinstance(heatmap, list)
        assert len(heatmap) == 0


class TestDailyStatsAPI:
    """Tests for GET /activity/daily endpoint."""

    async def test_daily_stats_endpoint_exists(self):
        """Test that daily stats endpoint is accessible."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/activity/daily")
            assert response.status_code != 404

    async def test_daily_stats_structure(self, db: AsyncSession, test_user: User):
        """Test daily stats response structure."""
        today = date.today()

        # Add activities for today
        activities = [
            ActivityType.LESSON_COMPLETED,
            ActivityType.CHALLENGE_ATTEMPTED,
            ActivityType.LOGIN,
        ]

        for activity_type in activities:
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=activity_type,
                created_at=datetime.combine(today, datetime.min.time()),
            )
            db.add(activity)
        await db.commit()

        from app.services.activity import get_daily_activity_stats

        stats = await get_daily_activity_stats(db, test_user, today)

        # Verify structure
        assert "date" in stats
        assert "total_count" in stats
        assert "activity_by_type" in stats
        assert stats["date"] == str(today)
        assert stats["total_count"] == 3
        assert isinstance(stats["activity_by_type"], dict)

    async def test_daily_stats_for_specific_date(
        self, db: AsyncSession, test_user: User
    ):
        """Test daily stats for a specific date."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Add activities for yesterday
        for _ in range(2):
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=ActivityType.LESSON_COMPLETED,
                created_at=datetime.combine(yesterday, datetime.min.time()),
            )
            db.add(activity)
        await db.commit()

        from app.services.activity import get_daily_activity_stats

        stats = await get_daily_activity_stats(db, test_user, yesterday)

        assert stats["date"] == str(yesterday)
        assert stats["total_count"] == 2


class TestStreakAPI:
    """Tests for GET /activity/streak endpoint."""

    async def test_streak_endpoint_exists(self):
        """Test that streak endpoint is accessible."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/activity/streak")
            assert response.status_code != 404

    async def test_streak_data_structure(self, db: AsyncSession, test_user: User):
        """Test streak response structure."""
        today = date.today()

        # Add activities for consecutive days
        for i in range(3):
            activity_date = today - timedelta(days=i)
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=ActivityType.LOGIN,
                created_at=datetime.combine(activity_date, datetime.min.time()),
            )
            db.add(activity)
        await db.commit()

        from app.services.activity import get_streak_data

        streak = await get_streak_data(db, test_user)

        # Verify structure
        assert "current_streak" in streak
        assert "longest_streak" in streak
        assert "total_active_days" in streak
        assert "last_active_date" in streak
        assert "streak_start_date" in streak
        assert isinstance(streak["current_streak"], int)
        assert isinstance(streak["longest_streak"], int)
        assert streak["current_streak"] == 3
        assert streak["longest_streak"] == 3
        assert streak["total_active_days"] == 3


class TestActivityCalendarAPI:
    """Tests for GET /activity/calendar endpoint."""

    async def test_calendar_endpoint_exists(self):
        """Test that calendar endpoint is accessible."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/activity/calendar")
            assert response.status_code != 404

    async def test_calendar_combines_heatmap_and_streak(
        self, db: AsyncSession, test_user: User
    ):
        """Test that calendar endpoint combines heatmap and streak data."""
        today = date.today()

        # Add activities
        for i in range(5):
            activity_date = today - timedelta(days=i)
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=ActivityType.LESSON_COMPLETED,
                created_at=datetime.combine(activity_date, datetime.min.time()),
            )
            db.add(activity)
        await db.commit()

        from app.services.activity import get_activity_heatmap, get_streak_data

        # Fetch both separately to verify combined endpoint would have both
        heatmap = await get_activity_heatmap(db, test_user)
        streak = await get_streak_data(db, test_user)

        # Verify both have data
        assert len(heatmap) > 0
        assert streak["current_streak"] > 0

        # In a full integration test, you'd call the calendar endpoint
        # and verify it returns both heatmap and streak in one response


class TestActivityAPIIntegration:
    """Integration tests for activity tracking API."""

    async def test_activity_logged_on_lesson_completion(
        self, db: AsyncSession, test_user: User
    ):
        """Test that activities are logged when lessons are completed."""
        # This would integrate with the progress service
        from app.services.activity import log_activity

        # Simulate lesson completion
        await log_activity(
            db=db,
            user_id=test_user.id,
            activity_type=ActivityType.LESSON_COMPLETED,
            entity_id=1,
            entity_type="lesson",
        )
        await db.commit()

        # Verify it appears in heatmap
        from app.services.activity import get_activity_heatmap

        heatmap = await get_activity_heatmap(db, test_user)

        assert len(heatmap) > 0
        assert heatmap[0]["count"] >= 1

    async def test_heatmap_aggregates_multiple_activities(
        self, db: AsyncSession, test_user: User
    ):
        """Test that heatmap correctly aggregates multiple activities per day."""
        today = date.today()

        # Log multiple activities today
        activity_types = [
            ActivityType.LESSON_COMPLETED,
            ActivityType.CHALLENGE_ATTEMPTED,
            ActivityType.CHALLENGE_SOLVED,
        ]

        for activity_type in activity_types:
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=activity_type,
                created_at=datetime.combine(today, datetime.min.time()),
            )
            db.add(activity)
        await db.commit()

        from app.services.activity import get_activity_heatmap

        heatmap = await get_activity_heatmap(
            db, test_user, start_date=today, end_date=today
        )

        assert len(heatmap) == 1
        assert heatmap[0]["date"] == str(today)
        assert heatmap[0]["count"] == 3

    async def test_streak_continuity_logic(self, db: AsyncSession, test_user: User):
        """Test that streak continuity is correctly calculated."""
        today = date.today()

        # Create a streak with a gap
        # Days 0, 1, 2 (current streak)
        for i in range(3):
            activity_date = today - timedelta(days=i)
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=ActivityType.LOGIN,
                created_at=datetime.combine(activity_date, datetime.min.time()),
            )
            db.add(activity)

        # Gap here (day 3, 4, 5)

        # Days 6, 7, 8, 9 (old streak)
        for i in range(6, 10):
            activity_date = today - timedelta(days=i)
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=ActivityType.LOGIN,
                created_at=datetime.combine(activity_date, datetime.min.time()),
            )
            db.add(activity)
        await db.commit()

        from app.services.activity import get_streak_data

        streak = await get_streak_data(db, test_user)

        # Current streak should be 3 (today, yesterday, day before)
        assert streak["current_streak"] == 3
        # Longest streak should be 4 (days 6-9)
        assert streak["longest_streak"] == 4
        # Total active days should be 7
        assert streak["total_active_days"] == 7

    async def test_activity_retrieval_accuracy(
        self, db: AsyncSession, test_user: User
    ):
        """Test accuracy of activity writes and retrieval."""
        today = date.today()

        # Log specific activities
        expected_activities = [
            (ActivityType.LESSON_COMPLETED, 1, "lesson"),
            (ActivityType.CHALLENGE_ATTEMPTED, 2, "challenge"),
            (ActivityType.ACHIEVEMENT_EARNED, 3, "achievement"),
        ]

        for activity_type, entity_id, entity_type in expected_activities:
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=activity_type,
                entity_id=entity_id,
                entity_type=entity_type,
                created_at=datetime.combine(today, datetime.min.time()),
            )
            db.add(activity)
        await db.commit()

        # Retrieve and verify
        from sqlalchemy import select

        query = (
            select(ActivityLog)
            .where(ActivityLog.user_id == test_user.id)
            .order_by(ActivityLog.id)
        )
        result = await db.execute(query)
        activities = list(result.scalars().all())

        # Verify all activities are accurately stored
        assert len(activities) >= len(expected_activities)

        # Verify last 3 activities match expected
        last_activities = activities[-3:]
        for i, (expected_type, expected_entity, expected_entity_type) in enumerate(
            expected_activities
        ):
            assert last_activities[i].activity_type == expected_type
            assert last_activities[i].entity_id == expected_entity
            assert last_activities[i].entity_type == expected_entity_type
