from datetime import datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.database import (
    Achievement,
    AchievementType,
    Base,
    Lesson,
    Module,
    ProgressStatus,
    User,
    UserAchievement,
    UserProgress,
)
from app.services.achievements import evaluate_achievements, get_user_achievements


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
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    import random
    user = User(
        telegram_id=random.randint(100000000, 999999999),
        username="testuser",
        first_name="Test",
        last_name="User",
        xp=0,
        level=1,
        current_streak=0,
        longest_streak=0,
        total_queries=0,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_module(db_session: AsyncSession):
    """Create a test module."""
    module = Module(
        title="Test Module",
        description="Test module description",
        order=1,
        is_published=True,
    )
    db_session.add(module)
    await db_session.commit()
    await db_session.refresh(module)
    return module


@pytest.fixture
async def test_lessons(db_session: AsyncSession, test_module: Module):
    """Create test lessons."""
    lessons = []
    for i in range(15):
        lesson = Lesson(
            module_id=test_module.id,
            title=f"Lesson {i+1}",
            content="Test content",
            order=i + 1,
            estimated_duration=20,
            is_published=True,
        )
        db_session.add(lesson)
        lessons.append(lesson)
    
    await db_session.commit()
    for lesson in lessons:
        await db_session.refresh(lesson)
    return lessons


@pytest.fixture(scope="module")
async def test_achievements(engine):
    """Create test achievements."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as db_session:
        achievements_data = [
            {
                "code": "first_lesson",
                "type": AchievementType.LESSON_COMPLETED,
                "title": "First Steps",
                "description": "Complete your first lesson",
                "icon": "🎓",
                "points": 10,
                "criteria": "Complete any lesson",
            },
            {
                "code": "ten_lessons",
                "type": AchievementType.LESSON_COMPLETED,
                "title": "Dedicated Learner",
                "description": "Complete 10 lessons",
                "icon": "💪",
                "points": 100,
                "criteria": "Complete 10 lessons",
            },
            {
                "code": "module_1_complete",
                "type": AchievementType.MODULE_COMPLETED,
                "title": "Module Master",
                "description": "Complete module 1",
                "icon": "📚",
                "points": 50,
                "criteria": "Complete all lessons in module 1",
            },
            {
                "code": "streak_7",
                "type": AchievementType.STREAK,
                "title": "Weekly Streak",
                "description": "Study for 7 days in a row",
                "icon": "🔥",
                "points": 75,
                "criteria": "Maintain a 7-day streak",
            },
            {
                "code": "streak_30",
                "type": AchievementType.STREAK,
                "title": "Monthly Streak",
                "description": "Study for 30 days in a row",
                "icon": "🏆",
                "points": 300,
                "criteria": "Maintain a 30-day streak",
            },
            {
                "code": "challenge_master",
                "type": AchievementType.CHALLENGES_SOLVED,
                "title": "Challenge Master",
                "description": "Solve 50 challenges",
                "icon": "🎯",
                "points": 200,
                "criteria": "Solve 50 challenges",
            },
            {
                "code": "perfect_score",
                "type": AchievementType.MILESTONE,
                "title": "Perfect Score",
                "description": "Get it right on the first try",
                "icon": "⭐",
                "points": 25,
                "criteria": "Complete a lesson on first try",
            },
            {
                "code": "speed_runner",
                "type": AchievementType.MILESTONE,
                "title": "Speed Runner",
                "description": "Complete a lesson faster than estimated",
                "icon": "⚡",
                "points": 30,
                "criteria": "Complete lesson faster than estimated duration",
            },
            {
                "code": "night_owl",
                "type": AchievementType.MILESTONE,
                "title": "Night Owl",
                "description": "Complete a lesson after midnight",
                "icon": "🦉",
                "points": 15,
                "criteria": "Complete lesson between 00:00 and 06:00",
            },
        ]
        
        achievements = []
        for data in achievements_data:
            achievement = Achievement(**data)
            db_session.add(achievement)
            achievements.append(achievement)
        
        await db_session.commit()
        for achievement in achievements:
            await db_session.refresh(achievement)
        return achievements


@pytest.mark.anyio
async def test_first_lesson_achievement(
    db_session: AsyncSession,
    test_user: User,
    test_lessons: list[Lesson],
    test_achievements: list[Achievement],
):
    """Test that first_lesson achievement is unlocked after completing one lesson."""
    # Complete one lesson
    progress = UserProgress(
        user_id=test_user.id,
        lesson_id=test_lessons[0].id,
        status=ProgressStatus.COMPLETED,
        attempts=1,
        first_try=True,
        xp_earned=75,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )
    db_session.add(progress)
    await db_session.commit()
    
    # Evaluate achievements
    newly_unlocked = await evaluate_achievements(db_session, test_user)
    
    # Check that first_lesson was unlocked
    assert len(newly_unlocked) == 2  # first_lesson and perfect_score
    codes = {a.achievement_code for a in newly_unlocked}
    assert "first_lesson" in codes
    assert "perfect_score" in codes
    
    # Verify in database
    query = select(UserAchievement).where(UserAchievement.user_id == test_user.id)
    result = await db_session.execute(query)
    user_achievements = list(result.scalars().all())
    assert len(user_achievements) == 2


@pytest.mark.anyio
async def test_ten_lessons_achievement(
    db_session: AsyncSession,
    test_user: User,
    test_lessons: list[Lesson],
    test_achievements: list[Achievement],
):
    """Test that ten_lessons achievement is unlocked after completing 10 lessons."""
    # Complete 10 lessons
    for i in range(10):
        progress = UserProgress(
            user_id=test_user.id,
            lesson_id=test_lessons[i].id,
            status=ProgressStatus.COMPLETED,
            attempts=2,
            first_try=False,
            xp_earned=50,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        db_session.add(progress)
    await db_session.commit()
    
    # Evaluate achievements
    newly_unlocked = await evaluate_achievements(db_session, test_user)
    
    # Check that ten_lessons was unlocked
    codes = {a.achievement_code for a in newly_unlocked}
    assert "ten_lessons" in codes
    assert "first_lesson" in codes


@pytest.mark.anyio
async def test_module_complete_achievement(
    db_session: AsyncSession,
    test_user: User,
    test_module: Module,
    test_lessons: list[Lesson],
    test_achievements: list[Achievement],
):
    """Test that module_1_complete achievement is unlocked after completing all lessons in module."""
    # Complete all lessons in module
    for lesson in test_lessons:
        progress = UserProgress(
            user_id=test_user.id,
            lesson_id=lesson.id,
            status=ProgressStatus.COMPLETED,
            attempts=1,
            first_try=True,
            xp_earned=75,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        db_session.add(progress)
    await db_session.commit()
    
    # Evaluate achievements
    newly_unlocked = await evaluate_achievements(db_session, test_user)
    
    # Check that module_1_complete was unlocked
    codes = {a.achievement_code for a in newly_unlocked}
    assert "module_1_complete" in codes


@pytest.mark.anyio
async def test_streak_achievements(
    db_session: AsyncSession,
    test_user: User,
    test_achievements: list[Achievement],
):
    """Test that streak achievements are unlocked based on current_streak."""
    # Set 7-day streak
    test_user.current_streak = 7
    await db_session.commit()
    
    # Evaluate achievements
    newly_unlocked = await evaluate_achievements(db_session, test_user)
    
    # Check that streak_7 was unlocked
    codes = {a.achievement_code for a in newly_unlocked}
    assert "streak_7" in codes
    assert "streak_30" not in codes
    
    # Now set 30-day streak
    test_user.current_streak = 30
    await db_session.commit()
    
    # Evaluate achievements again
    newly_unlocked = await evaluate_achievements(db_session, test_user)
    
    # Check that streak_30 was unlocked
    codes = {a.achievement_code for a in newly_unlocked}
    assert "streak_30" in codes


@pytest.mark.anyio
async def test_challenge_master_achievement(
    db_session: AsyncSession,
    test_user: User,
    test_achievements: list[Achievement],
):
    """Test that challenge_master is unlocked after 50 queries."""
    # Set total queries
    test_user.total_queries = 50
    await db_session.commit()
    
    # Evaluate achievements
    newly_unlocked = await evaluate_achievements(db_session, test_user)
    
    # Check that challenge_master was unlocked
    codes = {a.achievement_code for a in newly_unlocked}
    assert "challenge_master" in codes


@pytest.mark.anyio
async def test_perfect_score_achievement(
    db_session: AsyncSession,
    test_user: User,
    test_lessons: list[Lesson],
    test_achievements: list[Achievement],
):
    """Test that perfect_score is unlocked when completing lesson on first try."""
    # Complete one lesson on first try
    progress = UserProgress(
        user_id=test_user.id,
        lesson_id=test_lessons[0].id,
        status=ProgressStatus.COMPLETED,
        attempts=1,
        first_try=True,
        xp_earned=75,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )
    db_session.add(progress)
    await db_session.commit()
    
    # Evaluate achievements
    newly_unlocked = await evaluate_achievements(db_session, test_user)
    
    # Check that perfect_score was unlocked
    codes = {a.achievement_code for a in newly_unlocked}
    assert "perfect_score" in codes


@pytest.mark.anyio
async def test_speed_runner_achievement(
    db_session: AsyncSession,
    test_user: User,
    test_lessons: list[Lesson],
    test_achievements: list[Achievement],
):
    """Test that speed_runner is unlocked when completing lesson faster than estimated."""
    # Complete lesson in 10 minutes (estimated is 20)
    started_at = datetime.utcnow()
    completed_at = started_at + timedelta(minutes=10)
    
    progress = UserProgress(
        user_id=test_user.id,
        lesson_id=test_lessons[0].id,
        status=ProgressStatus.COMPLETED,
        attempts=1,
        first_try=True,
        xp_earned=75,
        started_at=started_at,
        completed_at=completed_at,
    )
    db_session.add(progress)
    await db_session.commit()
    
    # Evaluate achievements
    newly_unlocked = await evaluate_achievements(db_session, test_user)
    
    # Check that speed_runner was unlocked
    codes = {a.achievement_code for a in newly_unlocked}
    assert "speed_runner" in codes


@pytest.mark.anyio
async def test_night_owl_achievement(
    db_session: AsyncSession,
    test_user: User,
    test_lessons: list[Lesson],
    test_achievements: list[Achievement],
):
    """Test that night_owl is unlocked when completing lesson between 00:00 and 06:00."""
    # Complete lesson at 2 AM
    completed_at = datetime.utcnow().replace(hour=2, minute=0, second=0)
    
    progress = UserProgress(
        user_id=test_user.id,
        lesson_id=test_lessons[0].id,
        status=ProgressStatus.COMPLETED,
        attempts=1,
        first_try=True,
        xp_earned=75,
        started_at=completed_at - timedelta(minutes=10),
        completed_at=completed_at,
    )
    db_session.add(progress)
    await db_session.commit()
    
    # Evaluate achievements
    newly_unlocked = await evaluate_achievements(db_session, test_user)
    
    # Check that night_owl was unlocked
    codes = {a.achievement_code for a in newly_unlocked}
    assert "night_owl" in codes


@pytest.mark.anyio
async def test_achievement_only_unlocked_once(
    db_session: AsyncSession,
    test_user: User,
    test_lessons: list[Lesson],
    test_achievements: list[Achievement],
):
    """Test that achievements are only unlocked once."""
    # Complete one lesson
    progress = UserProgress(
        user_id=test_user.id,
        lesson_id=test_lessons[0].id,
        status=ProgressStatus.COMPLETED,
        attempts=1,
        first_try=True,
        xp_earned=75,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )
    db_session.add(progress)
    await db_session.commit()
    
    # First evaluation
    newly_unlocked_1 = await evaluate_achievements(db_session, test_user)
    assert len(newly_unlocked_1) > 0
    
    # Second evaluation should not unlock again
    newly_unlocked_2 = await evaluate_achievements(db_session, test_user)
    assert len(newly_unlocked_2) == 0


@pytest.mark.anyio
async def test_get_user_achievements_with_progress(
    db_session: AsyncSession,
    test_user: User,
    test_lessons: list[Lesson],
    test_achievements: list[Achievement],
):
    """Test getting user achievements with progress indicators."""
    # Complete 5 lessons (halfway to ten_lessons)
    for i in range(5):
        progress = UserProgress(
            user_id=test_user.id,
            lesson_id=test_lessons[i].id,
            status=ProgressStatus.COMPLETED,
            attempts=2,
            first_try=False,
            xp_earned=50,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        db_session.add(progress)
    await db_session.commit()
    
    # Unlock first_lesson achievement
    await evaluate_achievements(db_session, test_user)
    
    # Get achievements with status
    result = await get_user_achievements(db_session, test_user)
    
    assert result["total_earned"] == 1  # Only first_lesson
    
    # Find ten_lessons achievement
    ten_lessons = next(
        (a for a in result["achievements"] if a.code == "ten_lessons"),
        None,
    )
    assert ten_lessons is not None
    assert ten_lessons.is_earned is False
    assert ten_lessons.progress is not None
    assert ten_lessons.progress.current == 5
    assert ten_lessons.progress.target == 10
    assert ten_lessons.progress.percentage == 50.0


@pytest.mark.anyio
async def test_get_user_achievements_total_points(
    db_session: AsyncSession,
    test_user: User,
    test_lessons: list[Lesson],
    test_achievements: list[Achievement],
):
    """Test that total points are calculated correctly."""
    # Complete one lesson to unlock first_lesson and perfect_score
    progress = UserProgress(
        user_id=test_user.id,
        lesson_id=test_lessons[0].id,
        status=ProgressStatus.COMPLETED,
        attempts=1,
        first_try=True,
        xp_earned=75,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )
    db_session.add(progress)
    await db_session.commit()
    
    await evaluate_achievements(db_session, test_user)
    
    result = await get_user_achievements(db_session, test_user)
    
    # first_lesson (10) + perfect_score (25) = 35
    assert result["total_points"] == 35
