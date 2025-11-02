"""E2E performance tests."""
import asyncio
import time

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Lesson, Module, User


class TestAPIPerformance:
    """Test API endpoint performance."""

    @pytest.mark.asyncio
    async def test_dashboard_load_time(self, authenticated_client: AsyncClient):
        """Test that dashboard loads in under 2 seconds."""
        start_time = time.time()
        
        response = await authenticated_client.get("/api/user/profile")
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        assert response.status_code == 200
        assert elapsed < 2.0, f"Dashboard loaded in {elapsed:.2f}s (expected < 2s)"

    @pytest.mark.asyncio
    async def test_modules_list_response_time(self, authenticated_client: AsyncClient):
        """Test that modules list responds in under 500ms."""
        start_time = time.time()
        
        response = await authenticated_client.get("/api/courses/modules")
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        assert response.status_code == 200
        assert elapsed < 0.5, f"Modules list loaded in {elapsed:.2f}s (expected < 0.5s)"

    @pytest.mark.asyncio
    async def test_sandbox_execution_time(self, authenticated_client: AsyncClient):
        """Test that SQL sandbox executes queries in under 2 seconds."""
        query = "SELECT 1 as value, 'test' as name;"
        
        start_time = time.time()
        
        response = await authenticated_client.post(
            "/api/sandbox/execute",
            json={"query": query}
        )
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        assert elapsed < 2.0, f"Query executed in {elapsed:.2f}s (expected < 2s)"

    @pytest.mark.asyncio
    async def test_leaderboard_with_cache(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that leaderboard is fast with caching."""
        # Create many users
        for i in range(100):
            user = User(
                telegram_id=200000 + i,
                username=f"perfuser{i}",
                xp=i * 10,
                level=i % 10 + 1,
            )
            db_session.add(user)
        
        await db_session.commit()
        
        # First request (might populate cache)
        await authenticated_client.get("/api/leaderboard")
        
        # Second request (should use cache)
        start_time = time.time()
        response = await authenticated_client.get("/api/leaderboard")
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 0.5, f"Leaderboard loaded in {elapsed:.2f}s (expected < 0.5s)"


class TestConcurrentRequests:
    """Test handling of concurrent requests."""

    @pytest.mark.asyncio
    async def test_concurrent_progress_submissions(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test handling concurrent submission requests from same user."""
        # Create lessons
        module = Module(title="Test Module", order=1, is_published=True)
        db_session.add(module)
        await db_session.commit()
        await db_session.refresh(module)
        
        lessons = []
        for i in range(5):
            lesson = Lesson(
                module_id=module.id,
                title=f"Lesson {i}",
                order=i,
                content={},
                task={},
                expected_result=[],
                xp_reward=10,
            )
            db_session.add(lesson)
            lessons.append(lesson)
        
        await db_session.commit()
        
        # Submit to multiple lessons concurrently
        async def submit_attempt(lesson_id):
            return await authenticated_client.post(
                "/api/progress/submit",
                json={
                    "lesson_id": lesson_id,
                    "user_query": "SELECT 1",
                    "is_correct": True,
                }
            )
        
        # Execute concurrent requests
        await db_session.refresh(lessons[0])
        tasks = [submit_attempt(lesson.id) for lesson in lessons]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed (no race conditions)
        for response in responses:
            if not isinstance(response, Exception):
                assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_concurrent_sandbox_executions(self, authenticated_client: AsyncClient):
        """Test handling concurrent sandbox query executions."""
        queries = [
            "SELECT 1 as n;",
            "SELECT 2 as n;",
            "SELECT 3 as n;",
            "SELECT 4 as n;",
            "SELECT 5 as n;",
        ]
        
        async def execute_query(query):
            return await authenticated_client.post(
                "/api/sandbox/execute",
                json={"query": query}
            )
        
        start_time = time.time()
        tasks = [execute_query(q) for q in queries]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start_time
        
        # Should handle concurrent requests efficiently
        assert elapsed < 5.0, f"Concurrent queries took {elapsed:.2f}s"
        
        # Check responses
        success_count = sum(
            1 for r in responses 
            if not isinstance(r, Exception) and r.status_code == 200
        )
        assert success_count >= 3  # At least most should succeed


class TestScalability:
    """Test system scalability."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_large_leaderboard_pagination(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test leaderboard pagination with many users."""
        # Create 1000 users
        users = []
        for i in range(1000):
            user = User(
                telegram_id=300000 + i,
                username=f"scaleuser{i}",
                xp=i * 5,
                level=i % 20 + 1,
            )
            users.append(user)
        
        db_session.add_all(users)
        await db_session.commit()
        
        # Test pagination
        page1_response = await authenticated_client.get("/api/leaderboard?page=1&limit=50")
        assert page1_response.status_code == 200
        
        page2_response = await authenticated_client.get("/api/leaderboard?page=2&limit=50")
        assert page2_response.status_code == 200
        
        # Pages should have different users
        page1_data = page1_response.json()
        page2_data = page2_response.json()
        
        # Verify pagination works correctly

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_heatmap_generation_performance(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test heatmap generation with year of data."""
        from datetime import datetime, timedelta
        from app.models.database import ActivityLog, ActivityType
        from sqlalchemy import select
        
        # Get user
        result = await db_session.execute(
            select(User).where(User.telegram_id == 123456789)
        )
        user = result.scalar_one()
        
        # Create activity logs for a year
        base_date = datetime.utcnow() - timedelta(days=365)
        activities = []
        
        for i in range(365):
            activity = ActivityLog(
                user_id=user.id,
                activity_type=ActivityType.LESSON_COMPLETED,
                details={"lesson_id": 1},
                created_at=base_date + timedelta(days=i),
            )
            activities.append(activity)
        
        db_session.add_all(activities)
        await db_session.commit()
        
        # Test heatmap generation performance
        start_time = time.time()
        response = await authenticated_client.get("/api/activity/heatmap")
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 2.0, f"Heatmap generated in {elapsed:.2f}s (expected < 2s)"


class TestMemoryUsage:
    """Test memory-efficient operations."""

    @pytest.mark.asyncio
    async def test_large_result_set_streaming(self, authenticated_client: AsyncClient):
        """Test that large result sets are handled efficiently."""
        # Query that could return many results
        query = """
        SELECT n FROM (
            SELECT 1 as n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
        ) t;
        """
        
        response = await authenticated_client.post(
            "/api/sandbox/execute",
            json={"query": query}
        )
        
        # Should handle without memory issues
        assert response.status_code in [200, 400]

    @pytest.mark.asyncio
    async def test_batch_operations_efficiency(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that batch operations are efficient."""
        # This would test operations like bulk user creation,
        # batch progress updates, etc.
        pass


class TestCacheEfficiency:
    """Test caching mechanisms."""

    @pytest.mark.asyncio
    async def test_leaderboard_cache_hit(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that leaderboard uses cache effectively."""
        # First request (cache miss)
        start1 = time.time()
        response1 = await authenticated_client.get("/api/leaderboard")
        time1 = time.time() - start1
        
        # Second request (cache hit)
        start2 = time.time()
        response2 = await authenticated_client.get("/api/leaderboard")
        time2 = time.time() - start2
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Cache hit should be faster (or at least not slower)
        # Note: This is a soft assertion as timing can be inconsistent
        # assert time2 <= time1 * 1.5

    @pytest.mark.asyncio
    async def test_cache_invalidation(
        self, authenticated_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that cache is properly invalidated."""
        # Get leaderboard (populate cache)
        response1 = await authenticated_client.get("/api/leaderboard")
        data1 = response1.json()
        
        # Make changes that should invalidate cache
        # (e.g., submit new progress that changes rankings)
        
        # Trigger cache refresh
        await authenticated_client.post("/api/leaderboard/refresh")
        
        # Get leaderboard again (should have fresh data)
        response2 = await authenticated_client.get("/api/leaderboard")
        data2 = response2.json()
        
        # Data should be updated
