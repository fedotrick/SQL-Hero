import asyncio
from datetime import date, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.database import (
    ActivityLog,
    ActivityType,
    Base,
    Lesson,
    Module,
    ProgressStatus,
    User,
    UserProgress,
)
from app.services.progress import (
    calculate_level_from_xp,
    calculate_xp_for_lesson,
    calculate_xp_for_level,
    get_user_progress_summary,
    submit_lesson_attempt,
    update_user_streak,
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
        telegram_id=123456789,
        username="testuser",
        first_name="Test",
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


@pytest.fixture
async def test_module(db: AsyncSession):
    """Create a test module."""
    module = Module(
        title="Test Module",
        description="Test module for progress tracking",
        order=1,
        is_published=True,
    )
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return module


@pytest.fixture
async def test_lesson(db: AsyncSession, test_module: Module):
    """Create a test lesson."""
    lesson = Lesson(
        module_id=test_module.id,
        title="Test Lesson",
        content="Test lesson content",
        order=1,
        is_published=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return lesson


class TestXPAndLevelCalculations:
    """Tests for XP and level calculation formulas."""

    def test_calculate_xp_for_lesson_first_try(self):
        """Test XP calculation for first try success."""
        xp = calculate_xp_for_lesson(lesson_id=1, first_try=True)
        assert xp == 75  # 50 base + 25 bonus

    def test_calculate_xp_for_lesson_not_first_try(self):
        """Test XP calculation for repeated attempts."""
        xp = calculate_xp_for_lesson(lesson_id=1, first_try=False)
        assert xp == 50  # 50 base only

    def test_calculate_level_from_xp(self):
        """Test level calculation from XP."""
        assert calculate_level_from_xp(0) == 1
        assert calculate_level_from_xp(50) == 1
        assert calculate_level_from_xp(99) == 1
        assert calculate_level_from_xp(100) == 2
        assert calculate_level_from_xp(200) == 3
        assert calculate_level_from_xp(500) == 6

    def test_calculate_xp_for_level(self):
        """Test XP range calculation for levels."""
        current, next_level = calculate_xp_for_level(1)
        assert current == 0
        assert next_level == 100

        current, next_level = calculate_xp_for_level(2)
        assert current == 100
        assert next_level == 200

        current, next_level = calculate_xp_for_level(5)
        assert current == 400
        assert next_level == 500


class TestStreakLogic:
    """Tests for streak tracking logic."""

    @pytest.mark.anyio
    async def test_first_activity_sets_streak_to_1(self, db: AsyncSession, test_user: User):
        """Test that first activity sets streak to 1."""
        current, longest = await update_user_streak(db, test_user)
        assert current == 1
        assert longest == 1
        assert test_user.last_active_date is not None

    @pytest.mark.anyio
    async def test_activity_same_day_no_change(self, db: AsyncSession, test_user: User):
        """Test that multiple activities on same day don't change streak."""
        test_user.current_streak = 3
        test_user.longest_streak = 5
        test_user.last_active_date = datetime.utcnow()

        current, longest = await update_user_streak(db, test_user)
        assert current == 3
        assert longest == 5

    @pytest.mark.anyio
    async def test_activity_consecutive_day_increments(self, db: AsyncSession, test_user: User):
        """Test that activity on consecutive day increments streak."""
        yesterday = datetime.utcnow() - timedelta(days=1)
        test_user.current_streak = 3
        test_user.longest_streak = 5
        test_user.last_active_date = yesterday

        current, longest = await update_user_streak(db, test_user)
        assert current == 4
        assert longest == 5  # Doesn't exceed previous longest

    @pytest.mark.anyio
    async def test_streak_updates_longest(self, db: AsyncSession, test_user: User):
        """Test that streak updates longest when exceeded."""
        yesterday = datetime.utcnow() - timedelta(days=1)
        test_user.current_streak = 5
        test_user.longest_streak = 5
        test_user.last_active_date = yesterday

        current, longest = await update_user_streak(db, test_user)
        assert current == 6
        assert longest == 6

    @pytest.mark.anyio
    async def test_streak_resets_after_gap(self, db: AsyncSession, test_user: User):
        """Test that streak resets after missing days."""
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        test_user.current_streak = 10
        test_user.longest_streak = 10
        test_user.last_active_date = three_days_ago

        current, longest = await update_user_streak(db, test_user)
        assert current == 1
        assert longest == 10  # Longest is preserved


class TestLessonAttempts:
    """Tests for lesson attempt submission."""

    @pytest.mark.anyio
    async def test_first_successful_attempt_creates_progress(
        self, db: AsyncSession, test_user: User, test_lesson: Lesson
    ):
        """Test first successful attempt creates progress and awards XP."""
        result = await submit_lesson_attempt(
            db=db,
            user=test_user,
            lesson_id=test_lesson.id,
            user_query="SELECT * FROM test",
            success=True,
        )

        assert result["success"] is True
        assert result["xp_earned"] == 75  # First try bonus
        assert result["total_xp"] == 75
        assert result["level"] == 1
        assert result["first_try"] is True
        assert result["attempts"] == 1
        assert result["progress_status"] == "completed"
        assert test_user.total_queries == 1

    @pytest.mark.anyio
    async def test_first_failed_attempt_creates_progress_no_xp(
        self, db: AsyncSession, test_user: User, test_lesson: Lesson
    ):
        """Test first failed attempt creates progress but awards no XP."""
        result = await submit_lesson_attempt(
            db=db,
            user=test_user,
            lesson_id=test_lesson.id,
            user_query="INVALID SQL",
            success=False,
        )

        assert result["success"] is False
        assert result["xp_earned"] == 0
        assert result["attempts"] == 1
        assert result["first_try"] is False
        assert result["progress_status"] == "in_progress"

    @pytest.mark.anyio
    async def test_second_successful_attempt_awards_less_xp(
        self, db: AsyncSession, test_user: User, test_lesson: Lesson
    ):
        """Test second successful attempt awards XP without first try bonus."""
        # First attempt fails
        await submit_lesson_attempt(
            db=db,
            user=test_user,
            lesson_id=test_lesson.id,
            user_query="INVALID SQL",
            success=False,
        )

        # Second attempt succeeds
        result = await submit_lesson_attempt(
            db=db,
            user=test_user,
            lesson_id=test_lesson.id,
            user_query="SELECT * FROM test",
            success=True,
        )

        assert result["success"] is True
        assert result["xp_earned"] == 50  # No first try bonus
        assert result["first_try"] is False
        assert result["attempts"] == 2

    @pytest.mark.anyio
    async def test_completing_already_completed_lesson_no_xp(
        self, db: AsyncSession, test_user: User, test_lesson: Lesson
    ):
        """Test completing already completed lesson awards no additional XP."""
        # First successful attempt
        await submit_lesson_attempt(
            db=db,
            user=test_user,
            lesson_id=test_lesson.id,
            user_query="SELECT * FROM test",
            success=True,
        )

        xp_after_first = test_user.xp

        # Second successful attempt
        result = await submit_lesson_attempt(
            db=db,
            user=test_user,
            lesson_id=test_lesson.id,
            user_query="SELECT * FROM test",
            success=True,
        )

        assert result["success"] is True
        assert result["xp_earned"] == 0  # No additional XP
        assert test_user.xp == xp_after_first
        assert result["attempts"] == 2

    @pytest.mark.anyio
    async def test_level_up_on_xp_threshold(
        self, db: AsyncSession, test_user: User, test_lesson: Lesson
    ):
        """Test user levels up when XP crosses threshold."""
        # Set user to 90 XP (close to level 2)
        test_user.xp = 90
        test_user.level = 1

        result = await submit_lesson_attempt(
            db=db,
            user=test_user,
            lesson_id=test_lesson.id,
            user_query="SELECT * FROM test",
            success=True,
        )

        assert result["level_up"] is True
        assert result["level"] == 2
        assert result["total_xp"] == 165  # 90 + 75

    @pytest.mark.anyio
    async def test_multiple_attempts_increment_count(
        self, db: AsyncSession, test_user: User, test_lesson: Lesson
    ):
        """Test multiple attempts increment attempt counter."""
        for i in range(3):
            result = await submit_lesson_attempt(
                db=db,
                user=test_user,
                lesson_id=test_lesson.id,
                user_query="INVALID SQL",
                success=False,
            )
            assert result["attempts"] == i + 1

    @pytest.mark.anyio
    async def test_activity_log_created_on_completion(
        self, db: AsyncSession, test_user: User, test_lesson: Lesson
    ):
        """Test activity log is created when lesson is completed."""
        await submit_lesson_attempt(
            db=db,
            user=test_user,
            lesson_id=test_lesson.id,
            user_query="SELECT * FROM test",
            success=True,
        )

        # Check activity log
        query = select(ActivityLog).where(
            ActivityLog.user_id == test_user.id,
            ActivityLog.activity_type == ActivityType.LESSON_COMPLETED,
        )
        result = await db.execute(query)
        logs = list(result.scalars().all())

        assert len(logs) == 1
        assert logs[0].entity_id == test_lesson.id
        assert logs[0].entity_type == "lesson"

    @pytest.mark.anyio
    async def test_invalid_lesson_raises_error(self, db: AsyncSession, test_user: User):
        """Test attempting invalid lesson raises error."""
        with pytest.raises(ValueError, match="Lesson not found"):
            await submit_lesson_attempt(
                db=db,
                user=test_user,
                lesson_id=99999,
                user_query="SELECT * FROM test",
                success=True,
            )


class TestTransactionalIntegrity:
    """Tests for transactional handling and race condition prevention."""

    @pytest.mark.anyio
    async def test_concurrent_attempts_handled_correctly(
        self, db: AsyncSession, test_user: User, test_lesson: Lesson
    ):
        """Test that concurrent attempts are handled without data corruption."""
        # Note: This is a simplified test. In production, you'd want to test
        # with actual concurrent requests using multiple connections.

        result1 = await submit_lesson_attempt(
            db=db,
            user=test_user,
            lesson_id=test_lesson.id,
            user_query="SELECT * FROM test",
            success=True,
        )

        # Refresh to get latest state
        await db.refresh(test_user)

        result2 = await submit_lesson_attempt(
            db=db,
            user=test_user,
            lesson_id=test_lesson.id,
            user_query="SELECT * FROM test",
            success=True,
        )

        # Verify data integrity
        assert result1["attempts"] == 1
        assert result2["attempts"] == 2
        assert test_user.total_queries == 2

        # Verify XP awarded only once
        assert test_user.xp == 75  # Only first completion awards XP


class TestProgressSummary:
    """Tests for user progress summary endpoint."""

    @pytest.mark.anyio
    async def test_progress_summary_new_user(self, db: AsyncSession, test_user: User):
        """Test progress summary for new user with no progress."""
        summary = await get_user_progress_summary(db, test_user)

        assert summary["user_id"] == test_user.id
        assert summary["xp"] == 0
        assert summary["level"] == 1
        assert summary["current_streak"] == 0
        assert summary["longest_streak"] == 0
        assert summary["total_queries"] == 0
        assert summary["lessons_completed"] == 0
        assert summary["modules_completed"] == 0

    @pytest.mark.anyio
    async def test_progress_summary_with_completed_lessons(
        self, db: AsyncSession, test_user: User, test_lesson: Lesson
    ):
        """Test progress summary after completing lessons."""
        # Complete lesson
        await submit_lesson_attempt(
            db=db,
            user=test_user,
            lesson_id=test_lesson.id,
            user_query="SELECT * FROM test",
            success=True,
        )

        summary = await get_user_progress_summary(db, test_user)

        assert summary["lessons_completed"] == 1
        assert summary["xp"] == 75
        assert summary["level"] == 1
        assert summary["total_queries"] == 1
        assert summary["xp_to_next_level"] == 25  # 100 - 75

    @pytest.mark.anyio
    async def test_progress_summary_level_progress_percentage(
        self, db: AsyncSession, test_user: User, test_lesson: Lesson
    ):
        """Test progress percentage within level is calculated correctly."""
        test_user.xp = 150  # Level 2, halfway to level 3
        test_user.level = 2

        summary = await get_user_progress_summary(db, test_user)

        assert summary["level"] == 2
        assert summary["current_level_xp"] == 100
        assert summary["next_level_xp"] == 200
        assert summary["progress_percentage"] == 50.0  # 50 out of 100 XP

    @pytest.mark.anyio
    async def test_progress_summary_module_completion(
        self, db: AsyncSession, test_user: User, test_module: Module
    ):
        """Test module is marked complete when all lessons are done."""
        # Create multiple lessons in module
        lessons = []
        for i in range(3):
            lesson = Lesson(
                module_id=test_module.id,
                title=f"Lesson {i + 1}",
                order=i + 1,
                is_published=True,
            )
            db.add(lesson)
            lessons.append(lesson)
        await db.commit()

        # Complete all lessons
        for lesson in lessons:
            await db.refresh(lesson)
            await submit_lesson_attempt(
                db=db,
                user=test_user,
                lesson_id=lesson.id,
                user_query="SELECT * FROM test",
                success=True,
            )

        summary = await get_user_progress_summary(db, test_user)

        assert summary["lessons_completed"] == 3
        assert summary["modules_completed"] == 1
