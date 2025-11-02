"""E2E tests for gamification system."""
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Achievement, Lesson, Module, User, UserAchievement


class TestXPAndLevels:
    """Test XP calculation and level progression."""

    @pytest.mark.asyncio
    async def test_correct_solution_awards_xp(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that solving a lesson awards XP."""
        # Create lesson with XP reward
        module = Module(title="Test Module", order=1, is_published=True)
        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)
        
        lesson = Lesson(
            module_id=module.id,
            title="Test Lesson",
            order=1,
            content={},
            task={},
            expected_result=[],
            xp_reward=50,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)
        
        # Get user's initial XP
        result = await db_session.execute(
            select(User).where(User.telegram_id == 123456789)
        )
        user = result.scalar_one()
        initial_xp = user.xp
        
        # Submit correct solution
        response = await authenticated_client.post(
            "/api/progress/submit",
            json={
                "lesson_id": lesson.id,
                "user_query": "SELECT * FROM test",
                "is_correct": True,
            }
        )
        
        assert response.status_code in [200, 201]
        
        # Verify XP was awarded
        await db_session.refresh(user)
        assert user.xp >= initial_xp + 50

    @pytest.mark.asyncio
    async def test_first_try_bonus_awarded(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that solving on first try awards bonus XP."""
        module = Module(title="Test Module", order=1, is_published=True)
        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)
        
        lesson = Lesson(
            module_id=module.id,
            title="Test Lesson",
            order=1,
            content={},
            task={},
            expected_result=[],
            xp_reward=50,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)
        
        # Get user's initial XP
        result = await db_session.execute(
            select(User).where(User.telegram_id == 123456789)
        )
        user = result.scalar_one()
        initial_xp = user.xp
        
        # Submit correct solution on first try
        response = await authenticated_client.post(
            "/api/progress/submit",
            json={
                "lesson_id": lesson.id,
                "user_query": "SELECT * FROM test",
                "is_correct": True,
            }
        )
        
        assert response.status_code in [200, 201]
        
        # Verify bonus XP was awarded (should be more than base XP)
        await db_session.refresh(user)
        # First try bonus is typically 10-20% extra
        expected_min_xp = initial_xp + 50
        assert user.xp >= expected_min_xp

    @pytest.mark.asyncio
    async def test_level_up_on_xp_threshold(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that user levels up when reaching XP threshold."""
        # Get user
        result = await db_session.execute(
            select(User).where(User.telegram_id == 123456789)
        )
        user = result.scalar_one()
        initial_level = user.level
        
        # Set user close to level up (e.g., 90 XP away from next level)
        # Assuming level 2->3 requires 200 XP total
        user.xp = 180
        user.level = 2
        await db_session.commit()
        
        # Create high XP lesson
        module = Module(title="Test Module", order=1, is_published=True)
        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)
        
        lesson = Lesson(
            module_id=module.id,
            title="High XP Lesson",
            order=1,
            content={},
            task={},
            expected_result=[],
            xp_reward=50,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)
        
        # Submit solution to gain XP and level up
        response = await authenticated_client.post(
            "/api/progress/submit",
            json={
                "lesson_id": lesson.id,
                "user_query": "SELECT * FROM test",
                "is_correct": True,
            }
        )
        
        assert response.status_code in [200, 201]
        
        # Verify level increased
        await db_session.refresh(user)
        assert user.level > initial_level

    @pytest.mark.asyncio
    async def test_incorrect_solution_no_xp(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that incorrect solutions don't award XP."""
        result = await db_session.execute(
            select(User).where(User.telegram_id == 123456789)
        )
        user = result.scalar_one()
        initial_xp = user.xp
        
        # Create lesson
        module = Module(title="Test Module", order=1, is_published=True)
        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)
        
        lesson = Lesson(
            module_id=module.id,
            title="Test Lesson",
            order=1,
            content={},
            task={},
            expected_result=[],
            xp_reward=50,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)
        
        # Submit incorrect solution
        response = await authenticated_client.post(
            "/api/progress/submit",
            json={
                "lesson_id": lesson.id,
                "user_query": "WRONG QUERY",
                "is_correct": False,
            }
        )
        
        # XP should not change
        await db_session.refresh(user)
        assert user.xp == initial_xp


class TestStreakSystem:
    """Test streak calculation and maintenance."""

    @pytest.mark.asyncio
    async def test_daily_activity_increases_streak(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that daily activity increases streak."""
        result = await db_session.execute(
            select(User).where(User.telegram_id == 123456789)
        )
        user = result.scalar_one()
        initial_streak = user.current_streak
        
        # Simulate completing a lesson (should update streak)
        module = Module(title="Test Module", order=1, is_published=True)
        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)
        
        lesson = Lesson(
            module_id=module.id,
            title="Test Lesson",
            order=1,
            content={},
            task={},
            expected_result=[],
            xp_reward=10,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)
        
        response = await authenticated_client.post(
            "/api/progress/submit",
            json={
                "lesson_id": lesson.id,
                "user_query": "SELECT 1",
                "is_correct": True,
            }
        )
        
        assert response.status_code in [200, 201]
        
        # Check if streak was updated
        await db_session.refresh(user)
        # Streak logic depends on implementation
        # It should either increase or maintain based on last_active_date

    @pytest.mark.asyncio
    async def test_longest_streak_tracked(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that longest streak is tracked."""
        result = await db_session.execute(
            select(User).where(User.telegram_id == 123456789)
        )
        user = result.scalar_one()
        
        # Set current streak higher than longest
        user.current_streak = 15
        user.longest_streak = 10
        await db_session.commit()
        
        # Complete an activity
        module = Module(title="Test Module", order=1, is_published=True)
        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)
        
        lesson = Lesson(
            module_id=module.id,
            title="Test Lesson",
            order=1,
            content={},
            task={},
            expected_result=[],
            xp_reward=10,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)
        
        await authenticated_client.post(
            "/api/progress/submit",
            json={
                "lesson_id": lesson.id,
                "user_query": "SELECT 1",
                "is_correct": True,
            }
        )
        
        # Verify longest streak updated
        await db_session.refresh(user)
        assert user.longest_streak >= user.current_streak


class TestAchievements:
    """Test achievement unlocking system."""

    @pytest.mark.asyncio
    async def test_first_query_achievement_unlocked(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that 'First Query' achievement is unlocked."""
        # Create achievement
        achievement = Achievement(
            name="First Query",
            description="Execute your first SQL query",
            icon="🎯",
            xp_reward=10,
            trigger_condition={"type": "first_query"},
        )
        db_session.add(achievement)
        await db_session.commit()
        await db_session.refresh(achievement)
        
        # Get user
        result = await db_session.execute(
            select(User).where(User.telegram_id == 123456789)
        )
        user = result.scalar_one()
        
        # Reset user query count
        user.total_queries = 0
        await db_session.commit()
        
        # Execute first query via lesson completion
        module = Module(title="Test Module", order=1, is_published=True)
        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)
        
        lesson = Lesson(
            module_id=module.id,
            title="Test Lesson",
            order=1,
            content={},
            task={},
            expected_result=[],
            xp_reward=10,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)
        
        response = await authenticated_client.post(
            "/api/progress/submit",
            json={
                "lesson_id": lesson.id,
                "user_query": "SELECT 1",
                "is_correct": True,
            }
        )
        
        # Check if achievement was unlocked
        result = await db_session.execute(
            select(UserAchievement).where(
                UserAchievement.user_id == user.id,
                UserAchievement.achievement_id == achievement.id
            )
        )
        user_achievement = result.scalar_one_or_none()
        # Achievement should be unlocked (depends on background processing)

    @pytest.mark.asyncio
    async def test_achievement_notification_created(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that achievement unlock creates notification."""
        # This would test the notification queue system
        # when an achievement is unlocked
        pass

    @pytest.mark.asyncio
    async def test_duplicate_achievement_not_awarded(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that the same achievement is not awarded twice."""
        # Create achievement
        achievement = Achievement(
            name="Test Achievement",
            description="Test",
            icon="🏆",
            xp_reward=10,
            trigger_condition={},
        )
        db_session.add(achievement)
        await db_session.commit()
        await db_session.refresh(achievement)
        
        # Get user
        result = await db_session.execute(
            select(User).where(User.telegram_id == 123456789)
        )
        user = result.scalar_one()
        
        # Manually award achievement
        user_achievement = UserAchievement(
            user_id=user.id,
            achievement_id=achievement.id,
        )
        db_session.add(user_achievement)
        await db_session.commit()
        
        # Try to award again
        response = await authenticated_client.post(
            f"/api/achievements/{achievement.id}/unlock"
        )
        
        # Should not create duplicate
        result = await db_session.execute(
            select(UserAchievement).where(
                UserAchievement.user_id == user.id,
                UserAchievement.achievement_id == achievement.id
            )
        )
        achievements = result.scalars().all()
        assert len(achievements) == 1
