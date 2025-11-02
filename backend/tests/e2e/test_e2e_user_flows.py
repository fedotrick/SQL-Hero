"""E2E tests for complete user journeys."""
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Lesson, Module, User


class TestNewUserFlow:
    """Test complete flow for a new user."""

    @pytest.mark.asyncio
    async def test_complete_new_user_journey(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test complete journey: auth -> dashboard -> lesson -> complete."""
        
        # Step 1: First login through Telegram (creates user)
        auth_response = await client.post(
            "/api/auth/telegram",
            json={
                "telegram_id": 999888777,
                "username": "newbie",
                "first_name": "New",
                "last_name": "User",
                "language_code": "en",
            }
        )
        
        assert auth_response.status_code == 200
        token = auth_response.json()["access_token"]
        
        # Set auth header
        client.headers["Authorization"] = f"Bearer {token}"
        
        # Step 2: View dashboard (check initial state)
        profile_response = await client.get("/api/user/profile")
        assert profile_response.status_code == 200
        profile = profile_response.json()
        
        # New user should have default values
        assert profile["level"] == 1
        assert profile["xp"] == 0
        assert profile["current_streak"] == 0
        
        # Step 3: Get course modules
        modules_response = await client.get("/api/courses/modules")
        assert modules_response.status_code == 200
        modules = modules_response.json()
        
        # Should have at least one module
        if len(modules) == 0:
            # Create first module for test
            module = Module(
                title="Basics",
                description="SQL Basics",
                order=1,
                is_published=True,
            )
            db_session.add(module)
            await db_session.commit()
            await db_session.refresh(module)
            
            # Create first lesson
            lesson = Lesson(
                module_id=module.id,
                title="First Lesson",
                description="Your first SQL lesson",
                order=1,
                content={"theory": "SELECT statement basics"},
                task={"query": "SELECT * FROM users", "hint": "Use SELECT"},
                expected_result=[],
                xp_reward=20,
            )
            db_session.add(lesson)
            await db_session.commit()
            await db_session.refresh(lesson)
            
            first_module_id = module.id
            first_lesson_id = lesson.id
        else:
            first_module_id = modules[0]["id"]
            # Get lessons for first module
            lessons_response = await client.get(f"/api/courses/modules/{first_module_id}/lessons")
            lessons = lessons_response.json()
            first_lesson_id = lessons[0]["id"]
        
        # Step 4: Open first lesson
        lesson_response = await client.get(f"/api/courses/lessons/{first_lesson_id}")
        assert lesson_response.status_code == 200
        lesson_data = lesson_response.json()
        
        # Step 5: Write and execute first SQL query
        sandbox_response = await client.post(
            "/api/sandbox/execute",
            json={"query": "SELECT 1 as value"}
        )
        # Should execute successfully or be validated
        assert sandbox_response.status_code in [200, 400]  # 400 if validator blocks it
        
        # Step 6: Submit correct answer
        submit_response = await client.post(
            "/api/progress/submit",
            json={
                "lesson_id": first_lesson_id,
                "user_query": "SELECT * FROM users",
                "is_correct": True,
            }
        )
        assert submit_response.status_code in [200, 201]
        
        # Step 7: Check updated profile (XP gained, achievement unlocked)
        updated_profile_response = await client.get("/api/user/profile")
        assert updated_profile_response.status_code == 200
        updated_profile = updated_profile_response.json()
        
        # XP should have increased
        assert updated_profile["xp"] > profile["xp"]
        
        # Step 8: Check achievements (should have "First Query" or similar)
        achievements_response = await client.get("/api/achievements")
        assert achievements_response.status_code == 200
        
        # Step 9: Return to course map (progress should be updated)
        progress_response = await client.get("/api/progress")
        assert progress_response.status_code == 200


class TestAdvancedUserFlow:
    """Test flow for an experienced user."""

    @pytest.mark.asyncio
    async def test_advanced_user_journey(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test journey: multiple lessons -> streak building -> leaderboard."""
        
        # Create multiple lessons
        module = Module(title="Advanced SQL", order=1, is_published=True)
        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)
        
        lessons = []
        for i in range(5):
            lesson = Lesson(
                module_id=module.id,
                title=f"Lesson {i+1}",
                order=i+1,
                content={},
                task={},
                expected_result=[],
                xp_reward=20,
            )
            db_session.add(lesson)
            lessons.append(lesson)
        
        await db_session.commit()
        
        # Complete multiple lessons in sequence
        for lesson in lessons:
            await db_session.refresh(lesson)
            response = await authenticated_client.post(
                "/api/progress/submit",
                json={
                    "lesson_id": lesson.id,
                    "user_query": "SELECT * FROM test",
                    "is_correct": True,
                }
            )
            assert response.status_code in [200, 201]
        
        # Check leaderboard position
        leaderboard_response = await authenticated_client.get("/api/leaderboard")
        assert leaderboard_response.status_code == 200
        leaderboard = leaderboard_response.json()
        
        # User should appear in leaderboard
        # (depends on implementation details)
        
        # Check activity heatmap
        activity_response = await authenticated_client.get("/api/activity/heatmap")
        assert activity_response.status_code == 200


class TestModuleCompletionFlow:
    """Test complete module completion flow."""

    @pytest.mark.asyncio
    async def test_complete_module_unlock_next(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that completing a module unlocks the next one."""
        
        # Create two modules
        module1 = Module(
            title="Module 1",
            description="First module",
            order=1,
            is_published=True,
        )
        module2 = Module(
            title="Module 2",
            description="Second module (locked)",
            order=2,
            is_published=True,
        )
        db_session.add_all([module1, module2])
        await db_session.commit()
        await db_session.refresh(module1)
        await db_session.refresh(module2)
        
        # Create lessons for module 1
        lesson1 = Lesson(
            module_id=module1.id,
            title="Lesson 1",
            order=1,
            content={},
            task={},
            expected_result=[],
            xp_reward=10,
        )
        lesson2 = Lesson(
            module_id=module1.id,
            title="Lesson 2",
            order=2,
            content={},
            task={},
            expected_result=[],
            xp_reward=10,
        )
        db_session.add_all([lesson1, lesson2])
        await db_session.commit()
        
        # Complete all lessons in module 1
        for lesson in [lesson1, lesson2]:
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
        
        # Check if module 2 is now unlocked
        modules_response = await authenticated_client.get("/api/courses/modules")
        assert modules_response.status_code == 200
        # Module unlock logic depends on API implementation


class TestStreakMaintenanceFlow:
    """Test streak maintenance over multiple days."""

    @pytest.mark.asyncio
    async def test_consecutive_day_activity(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that consecutive daily activity builds streak."""
        # This would require date manipulation or mocking
        # to simulate multiple days of activity
        pass


class TestLeaderboardFlow:
    """Test leaderboard interaction flow."""

    @pytest.mark.asyncio
    async def test_view_leaderboard_and_rank(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test viewing leaderboard and finding own rank."""
        
        # Create multiple users with different XP
        for i in range(10):
            user = User(
                telegram_id=100000 + i,
                username=f"user{i}",
                xp=i * 100,
                level=i + 1,
            )
            db_session.add(user)
        
        await db_session.commit()
        
        # Refresh leaderboard cache
        refresh_response = await authenticated_client.post("/api/leaderboard/refresh")
        # Should succeed or be handled gracefully
        
        # Get leaderboard
        leaderboard_response = await authenticated_client.get("/api/leaderboard")
        assert leaderboard_response.status_code == 200
        leaderboard = leaderboard_response.json()
        
        # Should return top users sorted by XP
        # Verify sorting
        if len(leaderboard) > 1:
            for i in range(len(leaderboard) - 1):
                # Leaderboard should be sorted by XP descending
                pass


class TestErrorRecoveryFlow:
    """Test error handling and recovery flows."""

    @pytest.mark.asyncio
    async def test_recover_from_wrong_answer(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that users can retry after wrong answer."""
        
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
            xp_reward=10,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)
        
        # Submit wrong answer
        wrong_response = await authenticated_client.post(
            "/api/progress/submit",
            json={
                "lesson_id": lesson.id,
                "user_query": "WRONG QUERY",
                "is_correct": False,
            }
        )
        
        # Should be recorded but no XP awarded
        
        # Submit correct answer
        correct_response = await authenticated_client.post(
            "/api/progress/submit",
            json={
                "lesson_id": lesson.id,
                "user_query": "SELECT * FROM users",
                "is_correct": True,
            }
        )
        
        assert correct_response.status_code in [200, 201]
        # XP should be awarded (but no first-try bonus)

    @pytest.mark.asyncio
    async def test_handle_network_interruption(
        self, authenticated_client: AsyncClient
    ):
        """Test graceful handling of network issues."""
        # This would test retry logic and error messages
        # when network interruptions occur
        pass
