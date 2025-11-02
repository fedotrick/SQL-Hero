"""E2E tests for course API flow."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Lesson, Module, ProgressStatus, User, UserProgress


class TestCourseAPIFlow:
    """Test complete course API flow."""

    @pytest.mark.asyncio
    async def test_get_modules_list(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test getting modules list."""
        # Create test modules
        module1 = Module(
            title="Module 1: Basics",
            description="Learn SQL basics",
            order=1,
            is_published=True,
        )
        module2 = Module(
            title="Module 2: Advanced",
            description="Advanced SQL",
            order=2,
            is_published=True,
        )
        db_session.add_all([module1, module2])
        await db_session.commit()
        
        response = await authenticated_client.get("/api/courses/modules")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert data[0]["title"] == "Module 1: Basics"
        assert data[0]["order"] == 1

    @pytest.mark.asyncio
    async def test_get_module_lessons(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test getting lessons for a module."""
        # Create module with lessons
        module = Module(
            title="Test Module",
            description="Test",
            order=1,
            is_published=True,
        )
        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)
        
        lesson1 = Lesson(
            module_id=module.id,
            title="Lesson 1",
            description="First lesson",
            order=1,
            content={"theory": "SELECT basics"},
            task={"query": "SELECT * FROM users"},
            expected_result=[],
            xp_reward=10,
        )
        lesson2 = Lesson(
            module_id=module.id,
            title="Lesson 2",
            description="Second lesson",
            order=2,
            content={"theory": "WHERE clause"},
            task={"query": "SELECT * FROM users WHERE id=1"},
            expected_result=[],
            xp_reward=15,
        )
        db_session.add_all([lesson1, lesson2])
        await db_session.commit()
        
        response = await authenticated_client.get(f"/api/courses/modules/{module.id}/lessons")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Lesson 1"
        assert data[0]["xp_reward"] == 10

    @pytest.mark.asyncio
    async def test_get_lesson_detail(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test getting lesson details."""
        # Create lesson
        module = Module(title="Test Module", order=1, is_published=True)
        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)
        
        lesson = Lesson(
            module_id=module.id,
            title="Test Lesson",
            description="Test",
            order=1,
            content={"theory": "SQL basics", "examples": []},
            task={"query": "SELECT * FROM users", "hint": "Use SELECT"},
            expected_result=[{"id": 1, "name": "Test"}],
            xp_reward=20,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)
        
        response = await authenticated_client.get(f"/api/courses/lessons/{lesson.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Lesson"
        assert data["content"]["theory"] == "SQL basics"
        assert data["task"]["query"] == "SELECT * FROM users"
        assert data["xp_reward"] == 20


class TestCourseAccessControl:
    """Test course access control and locking."""

    @pytest.mark.asyncio
    async def test_unpublished_modules_not_visible(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that unpublished modules are not returned."""
        # Create published and unpublished modules
        published = Module(title="Published", order=1, is_published=True)
        unpublished = Module(title="Unpublished", order=2, is_published=False)
        db_session.add_all([published, unpublished])
        await db_session.commit()
        
        response = await authenticated_client.get("/api/courses/modules")
        
        assert response.status_code == 200
        data = response.json()
        titles = [m["title"] for m in data]
        assert "Published" in titles
        assert "Unpublished" not in titles

    @pytest.mark.asyncio
    async def test_lesson_locked_status_based_on_progress(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that lesson locked status is based on user progress."""
        # This test would check if lessons are locked based on completion of previous lessons
        # Implementation depends on the actual locking logic in the API
        pass


class TestCourseProgressTracking:
    """Test course progress tracking."""

    @pytest.mark.asyncio
    async def test_user_progress_tracked_for_lessons(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that user progress is tracked for lessons."""
        from sqlalchemy import select
        
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
        
        # Get current user
        result = await db_session.execute(
            select(User).where(User.telegram_id == 123456789)
        )
        user = result.scalar_one()
        
        # Submit attempt (this creates progress)
        attempt_data = {
            "lesson_id": lesson.id,
            "user_query": "SELECT * FROM users",
            "is_correct": True,
        }
        
        response = await authenticated_client.post("/api/progress/submit", json=attempt_data)
        assert response.status_code in [200, 201]
        
        # Verify progress was created
        result = await db_session.execute(
            select(UserProgress).where(
                UserProgress.user_id == user.id,
                UserProgress.lesson_id == lesson.id
            )
        )
        progress = result.scalar_one_or_none()
        assert progress is not None
        assert progress.status == ProgressStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_module_progress_aggregation(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that module progress is aggregated from lessons."""
        # This test would verify that completing all lessons in a module
        # updates the module's overall completion status
        pass
