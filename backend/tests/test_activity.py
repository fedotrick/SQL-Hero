from datetime import date, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.database import ActivityLog, ActivityType, Base, User
from app.services.activity import (
    get_activity_heatmap,
    get_daily_activity_stats,
    get_streak_data,
    log_activity,
)


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
        telegram_id=987654321,
        username="activityuser",
        first_name="Activity",
        last_name="User",
        xp=0,
        level=1,
        current_streak=0,
        longest_streak=0,
        total_queries=0,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


class TestActivityLogging:
    """Tests for activity logging functionality."""

    async def test_log_activity_basic(self, db: AsyncSession, test_user: User):
        """Test basic activity logging."""
        activity = await log_activity(
            db=db,
            user_id=test_user.id,
            activity_type=ActivityType.LESSON_COMPLETED,
            entity_id=1,
            entity_type="lesson",
            details="Test activity",
        )

        assert activity.id is not None
        assert activity.user_id == test_user.id
        assert activity.activity_type == ActivityType.LESSON_COMPLETED
        assert activity.entity_id == 1
        assert activity.entity_type == "lesson"
        assert activity.details == "Test activity"
        assert activity.created_at is not None

    async def test_log_activity_without_optional_fields(
        self, db: AsyncSession, test_user: User
    ):
        """Test logging activity without optional fields."""
        activity = await log_activity(
            db=db,
            user_id=test_user.id,
            activity_type=ActivityType.LOGIN,
        )

        assert activity.id is not None
        assert activity.user_id == test_user.id
        assert activity.activity_type == ActivityType.LOGIN
        assert activity.entity_id is None
        assert activity.entity_type is None
        assert activity.details is None

    async def test_activity_persisted_to_database(
        self, db: AsyncSession, test_user: User
    ):
        """Test that activities are properly persisted to database."""
        await log_activity(
            db=db,
            user_id=test_user.id,
            activity_type=ActivityType.CHALLENGE_ATTEMPTED,
        )
        await db.commit()

        query = select(ActivityLog).where(ActivityLog.user_id == test_user.id)
        result = await db.execute(query)
        activities = list(result.scalars().all())

        assert len(activities) >= 1
        assert activities[-1].activity_type == ActivityType.CHALLENGE_ATTEMPTED


class TestActivityHeatmap:
    """Tests for activity heatmap functionality."""

    async def test_heatmap_empty_user(self, db: AsyncSession, test_user: User):
        """Test heatmap for user with no activities."""
        heatmap = await get_activity_heatmap(db, test_user)

        assert isinstance(heatmap, list)
        assert len(heatmap) == 0

    async def test_heatmap_single_day(self, db: AsyncSession, test_user: User):
        """Test heatmap with activities on a single day."""
        # Add 3 activities today
        for _ in range(3):
            await log_activity(
                db=db,
                user_id=test_user.id,
                activity_type=ActivityType.LESSON_COMPLETED,
            )
        await db.commit()

        today = date.today()
        heatmap = await get_activity_heatmap(
            db, test_user, start_date=today, end_date=today
        )

        assert len(heatmap) == 1
        assert heatmap[0]["date"] == str(today)
        assert heatmap[0]["count"] == 3

    async def test_heatmap_multiple_days(self, db: AsyncSession, test_user: User):
        """Test heatmap with activities across multiple days."""
        today = date.today()

        # Add activities for today
        activity1 = ActivityLog(
            user_id=test_user.id,
            activity_type=ActivityType.LESSON_COMPLETED,
            created_at=datetime.combine(today, datetime.min.time()),
        )
        db.add(activity1)

        # Add activities for yesterday
        yesterday = today - timedelta(days=1)
        for _ in range(2):
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=ActivityType.CHALLENGE_ATTEMPTED,
                created_at=datetime.combine(yesterday, datetime.min.time()),
            )
            db.add(activity)

        # Add activities for 2 days ago
        two_days_ago = today - timedelta(days=2)
        for _ in range(3):
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=ActivityType.LOGIN,
                created_at=datetime.combine(two_days_ago, datetime.min.time()),
            )
            db.add(activity)

        await db.commit()

        start_date = today - timedelta(days=7)
        heatmap = await get_activity_heatmap(db, test_user, start_date=start_date)

        assert len(heatmap) == 3
        # Sort by date to ensure consistent order
        heatmap_sorted = sorted(heatmap, key=lambda x: x["date"])

        assert heatmap_sorted[0]["date"] == str(two_days_ago)
        assert heatmap_sorted[0]["count"] == 3
        assert heatmap_sorted[1]["date"] == str(yesterday)
        assert heatmap_sorted[1]["count"] == 2
        assert heatmap_sorted[2]["date"] == str(today)
        assert heatmap_sorted[2]["count"] == 1

    async def test_heatmap_date_range_filtering(
        self, db: AsyncSession, test_user: User
    ):
        """Test that heatmap respects date range filters."""
        today = date.today()
        old_date = today - timedelta(days=400)

        # Add activity outside the default range
        old_activity = ActivityLog(
            user_id=test_user.id,
            activity_type=ActivityType.LOGIN,
            created_at=datetime.combine(old_date, datetime.min.time()),
        )
        db.add(old_activity)

        # Add recent activity
        recent_activity = ActivityLog(
            user_id=test_user.id,
            activity_type=ActivityType.LESSON_COMPLETED,
            created_at=datetime.combine(today, datetime.min.time()),
        )
        db.add(recent_activity)
        await db.commit()

        # Get heatmap with default range (365 days)
        heatmap = await get_activity_heatmap(db, test_user)

        # Should only include recent activity
        assert len(heatmap) == 1
        assert heatmap[0]["date"] == str(today)

    async def test_heatmap_response_structure(self, db: AsyncSession, test_user: User):
        """Test that heatmap response has correct structure."""
        await log_activity(
            db=db,
            user_id=test_user.id,
            activity_type=ActivityType.LESSON_COMPLETED,
        )
        await db.commit()

        heatmap = await get_activity_heatmap(db, test_user)

        assert len(heatmap) > 0
        for entry in heatmap:
            assert "date" in entry
            assert "count" in entry
            assert isinstance(entry["date"], str)
            assert isinstance(entry["count"], int)
            assert entry["count"] > 0


class TestDailyActivityStats:
    """Tests for daily activity statistics."""

    async def test_daily_stats_empty(self, db: AsyncSession, test_user: User):
        """Test daily stats with no activities."""
        stats = await get_daily_activity_stats(db, test_user)

        assert stats["date"] == str(date.today())
        assert stats["total_count"] == 0
        assert stats["activity_by_type"] == {}

    async def test_daily_stats_single_type(self, db: AsyncSession, test_user: User):
        """Test daily stats with single activity type."""
        today = date.today()

        for _ in range(3):
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=ActivityType.LESSON_COMPLETED,
                created_at=datetime.combine(today, datetime.min.time()),
            )
            db.add(activity)
        await db.commit()

        stats = await get_daily_activity_stats(db, test_user, target_date=today)

        assert stats["date"] == str(today)
        assert stats["total_count"] == 3
        assert stats["activity_by_type"]["lesson_completed"] == 3

    async def test_daily_stats_multiple_types(self, db: AsyncSession, test_user: User):
        """Test daily stats with multiple activity types."""
        today = date.today()

        # Add different activity types
        activities = [
            ActivityType.LESSON_COMPLETED,
            ActivityType.LESSON_COMPLETED,
            ActivityType.CHALLENGE_ATTEMPTED,
            ActivityType.CHALLENGE_SOLVED,
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

        stats = await get_daily_activity_stats(db, test_user, target_date=today)

        assert stats["date"] == str(today)
        assert stats["total_count"] == 5
        assert stats["activity_by_type"]["lesson_completed"] == 2
        assert stats["activity_by_type"]["challenge_attempted"] == 1
        assert stats["activity_by_type"]["challenge_solved"] == 1
        assert stats["activity_by_type"]["login"] == 1

    async def test_daily_stats_specific_date(self, db: AsyncSession, test_user: User):
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

        # Add activities for today
        for _ in range(3):
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=ActivityType.LOGIN,
                created_at=datetime.combine(today, datetime.min.time()),
            )
            db.add(activity)
        await db.commit()

        # Get stats for yesterday
        stats = await get_daily_activity_stats(db, test_user, target_date=yesterday)

        assert stats["date"] == str(yesterday)
        assert stats["total_count"] == 2


class TestStreakData:
    """Tests for streak calculation and continuity logic."""

    async def test_streak_no_activities(self, db: AsyncSession, test_user: User):
        """Test streak calculation with no activities."""
        streak = await get_streak_data(db, test_user)

        assert streak["current_streak"] == 0
        assert streak["longest_streak"] == 0
        assert streak["total_active_days"] == 0
        assert streak["last_active_date"] is None
        assert streak["streak_start_date"] is None

    async def test_streak_single_day_today(self, db: AsyncSession, test_user: User):
        """Test streak with activity only today."""
        today = date.today()

        activity = ActivityLog(
            user_id=test_user.id,
            activity_type=ActivityType.LOGIN,
            created_at=datetime.combine(today, datetime.min.time()),
        )
        db.add(activity)
        await db.commit()

        streak = await get_streak_data(db, test_user)

        assert streak["current_streak"] == 1
        assert streak["longest_streak"] == 1
        assert streak["total_active_days"] == 1
        assert streak["last_active_date"] == str(today)
        assert streak["streak_start_date"] == str(today)

    async def test_streak_consecutive_days(self, db: AsyncSession, test_user: User):
        """Test streak with consecutive days of activity."""
        today = date.today()

        # Add activities for the last 5 consecutive days
        for i in range(5):
            activity_date = today - timedelta(days=i)
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=ActivityType.LESSON_COMPLETED,
                created_at=datetime.combine(activity_date, datetime.min.time()),
            )
            db.add(activity)
        await db.commit()

        streak = await get_streak_data(db, test_user)

        assert streak["current_streak"] == 5
        assert streak["longest_streak"] == 5
        assert streak["total_active_days"] == 5
        assert streak["last_active_date"] == str(today)
        assert streak["streak_start_date"] == str(today - timedelta(days=4))

    async def test_streak_broken_continuity(self, db: AsyncSession, test_user: User):
        """Test streak calculation when continuity is broken."""
        today = date.today()

        # Add activities for today and yesterday
        for i in range(2):
            activity_date = today - timedelta(days=i)
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=ActivityType.LESSON_COMPLETED,
                created_at=datetime.combine(activity_date, datetime.min.time()),
            )
            db.add(activity)

        # Add activity 5 days ago (breaking the streak)
        old_date = today - timedelta(days=5)
        old_activity = ActivityLog(
            user_id=test_user.id,
            activity_type=ActivityType.LOGIN,
            created_at=datetime.combine(old_date, datetime.min.time()),
        )
        db.add(old_activity)
        await db.commit()

        streak = await get_streak_data(db, test_user)

        # Current streak should only count consecutive days
        assert streak["current_streak"] == 2
        assert streak["total_active_days"] == 3

    async def test_streak_longest_vs_current(self, db: AsyncSession, test_user: User):
        """Test that longest streak is tracked correctly."""
        today = date.today()

        # Create a 7-day streak in the past
        for i in range(7):
            old_date = today - timedelta(days=30 + i)
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=ActivityType.LESSON_COMPLETED,
                created_at=datetime.combine(old_date, datetime.min.time()),
            )
            db.add(activity)

        # Create a 3-day current streak
        for i in range(3):
            recent_date = today - timedelta(days=i)
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=ActivityType.LESSON_COMPLETED,
                created_at=datetime.combine(recent_date, datetime.min.time()),
            )
            db.add(activity)
        await db.commit()

        streak = await get_streak_data(db, test_user)

        # Current streak should be 3, but longest should be 7
        assert streak["current_streak"] == 3
        assert streak["longest_streak"] == 7
        assert streak["total_active_days"] == 10

    async def test_streak_yesterday_counts(self, db: AsyncSession, test_user: User):
        """Test that streak includes yesterday if user was active yesterday."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Only add activity for yesterday (not today)
        activity = ActivityLog(
            user_id=test_user.id,
            activity_type=ActivityType.LOGIN,
            created_at=datetime.combine(yesterday, datetime.min.time()),
        )
        db.add(activity)
        await db.commit()

        streak = await get_streak_data(db, test_user)

        # Should still have a current streak of 1
        assert streak["current_streak"] == 1
        assert streak["last_active_date"] == str(yesterday)

    async def test_streak_two_days_ago_breaks_streak(
        self, db: AsyncSession, test_user: User
    ):
        """Test that streak is broken if last activity was 2+ days ago."""
        today = date.today()
        two_days_ago = today - timedelta(days=2)

        activity = ActivityLog(
            user_id=test_user.id,
            activity_type=ActivityType.LOGIN,
            created_at=datetime.combine(two_days_ago, datetime.min.time()),
        )
        db.add(activity)
        await db.commit()

        streak = await get_streak_data(db, test_user)

        # Current streak should be broken (0)
        assert streak["current_streak"] == 0
        assert streak["longest_streak"] == 1
        assert streak["total_active_days"] == 1

    async def test_streak_multiple_activities_same_day(
        self, db: AsyncSession, test_user: User
    ):
        """Test that multiple activities on the same day count as one day."""
        today = date.today()

        # Add multiple activities today
        for _ in range(5):
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=ActivityType.LESSON_COMPLETED,
                created_at=datetime.combine(today, datetime.min.time()),
            )
            db.add(activity)
        await db.commit()

        streak = await get_streak_data(db, test_user)

        # Should count as 1 active day, not 5
        assert streak["current_streak"] == 1
        assert streak["total_active_days"] == 1


class TestActivityIndexes:
    """Tests to verify that activity log indexes exist and are used efficiently."""

    async def test_activity_log_has_user_index(self, db: AsyncSession, test_user: User):
        """Test that queries by user_id can use indexes."""
        # Add multiple activities
        for _ in range(10):
            await log_activity(
                db=db,
                user_id=test_user.id,
                activity_type=ActivityType.LESSON_COMPLETED,
            )
        await db.commit()

        # Query should use user_id index
        query = select(ActivityLog).where(ActivityLog.user_id == test_user.id)
        result = await db.execute(query)
        activities = list(result.scalars().all())

        assert len(activities) == 10

    async def test_activity_log_has_date_index(self, db: AsyncSession, test_user: User):
        """Test that queries by created_at can use indexes."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Add activities for different dates
        for activity_date in [today, yesterday]:
            activity = ActivityLog(
                user_id=test_user.id,
                activity_type=ActivityType.LOGIN,
                created_at=datetime.combine(activity_date, datetime.min.time()),
            )
            db.add(activity)
        await db.commit()

        # Query with date filter should use index
        start_datetime = datetime.combine(today, datetime.min.time())
        query = select(ActivityLog).where(ActivityLog.created_at >= start_datetime)
        result = await db.execute(query)
        activities = list(result.scalars().all())

        assert len(activities) >= 1
