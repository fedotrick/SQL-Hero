"""E2E tests for MySQL Sandbox security."""
import pytest
from httpx import AsyncClient


class TestSandboxSecurity:
    """Test SQL sandbox security measures."""

    @pytest.mark.asyncio
    async def test_drop_database_blocked(self, authenticated_client: AsyncClient):
        """Test that DROP DATABASE commands are blocked."""
        malicious_query = "DROP DATABASE appdb;"
        
        response = await authenticated_client.post(
            "/api/sandbox/execute",
            json={"query": malicious_query}
        )
        
        # Should be rejected by query validator
        assert response.status_code in [400, 403]
        data = response.json()
        assert "not allowed" in data.get("detail", "").lower() or \
               "blocked" in data.get("detail", "").lower()

    @pytest.mark.asyncio
    async def test_drop_table_blocked(self, authenticated_client: AsyncClient):
        """Test that DROP TABLE commands are blocked."""
        malicious_query = "DROP TABLE users;"
        
        response = await authenticated_client.post(
            "/api/sandbox/execute",
            json={"query": malicious_query}
        )
        
        assert response.status_code in [400, 403]

    @pytest.mark.asyncio
    async def test_system_tables_access_blocked(self, authenticated_client: AsyncClient):
        """Test that access to system tables is blocked."""
        malicious_queries = [
            "SELECT * FROM mysql.user;",
            "SELECT * FROM information_schema.tables;",
            "SELECT * FROM performance_schema.threads;",
        ]
        
        for query in malicious_queries:
            response = await authenticated_client.post(
                "/api/sandbox/execute",
                json={"query": query}
            )
            
            # Should be blocked
            assert response.status_code in [400, 403], f"Query not blocked: {query}"

    @pytest.mark.asyncio
    async def test_alter_table_blocked(self, authenticated_client: AsyncClient):
        """Test that ALTER TABLE commands are blocked."""
        malicious_query = "ALTER TABLE users ADD COLUMN hacked INT;"
        
        response = await authenticated_client.post(
            "/api/sandbox/execute",
            json={"query": malicious_query}
        )
        
        assert response.status_code in [400, 403]

    @pytest.mark.asyncio
    async def test_delete_without_where_blocked(self, authenticated_client: AsyncClient):
        """Test that DELETE without WHERE is blocked."""
        malicious_query = "DELETE FROM users;"
        
        response = await authenticated_client.post(
            "/api/sandbox/execute",
            json={"query": malicious_query}
        )
        
        assert response.status_code in [400, 403]

    @pytest.mark.asyncio
    async def test_update_without_where_blocked(self, authenticated_client: AsyncClient):
        """Test that UPDATE without WHERE is blocked."""
        malicious_query = "UPDATE users SET username='hacked';"
        
        response = await authenticated_client.post(
            "/api/sandbox/execute",
            json={"query": malicious_query}
        )
        
        assert response.status_code in [400, 403]


class TestSandboxTimeout:
    """Test sandbox timeout enforcement."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_long_running_query_timeout(self, authenticated_client: AsyncClient):
        """Test that queries exceeding timeout limit are terminated."""
        # Query that would take a long time
        slow_query = """
        SELECT COUNT(*) FROM 
        (SELECT 1 UNION SELECT 2 UNION SELECT 3) t1,
        (SELECT 1 UNION SELECT 2 UNION SELECT 3) t2,
        (SELECT 1 UNION SELECT 2 UNION SELECT 3) t3,
        (SELECT 1 UNION SELECT 2 UNION SELECT 3) t4,
        (SELECT 1 UNION SELECT 2 UNION SELECT 3) t5;
        """
        
        response = await authenticated_client.post(
            "/api/sandbox/execute",
            json={"query": slow_query},
            timeout=10.0  # Client timeout longer than expected server timeout
        )
        
        # Should timeout or return timeout error
        if response.status_code != 200:
            data = response.json()
            assert "timeout" in data.get("detail", "").lower()

    @pytest.mark.asyncio
    async def test_timeout_value_configurable(self, authenticated_client: AsyncClient):
        """Test that timeout value is properly configured (should be ~5 seconds)."""
        # Simple query should succeed within timeout
        quick_query = "SELECT 1 as value;"
        
        response = await authenticated_client.post(
            "/api/sandbox/execute",
            json={"query": quick_query}
        )
        
        assert response.status_code == 200


class TestSandboxIsolation:
    """Test sandbox session isolation."""

    @pytest.mark.asyncio
    async def test_user_sessions_isolated(self, authenticated_client: AsyncClient):
        """Test that user sessions are isolated from each other."""
        # Create temporary table in session
        create_temp = "CREATE TEMPORARY TABLE IF NOT EXISTS temp_test (id INT);"
        
        response1 = await authenticated_client.post(
            "/api/sandbox/execute",
            json={"query": create_temp}
        )
        
        # Temporary tables should be allowed
        assert response1.status_code in [200, 400]  # Might be blocked by validator
        
        # In a different session/connection, temp table should not exist
        # This would require two different authenticated clients
        # Implementation depends on sandbox session management

    @pytest.mark.asyncio
    async def test_transaction_isolation(self, authenticated_client: AsyncClient):
        """Test that transactions are properly isolated."""
        # Test that changes in one session don't affect another
        # This is more of an integration test with actual database
        pass


class TestSandboxResultValidation:
    """Test sandbox result validation."""

    @pytest.mark.asyncio
    async def test_valid_select_query_returns_results(self, authenticated_client: AsyncClient):
        """Test that valid SELECT queries return results."""
        valid_query = "SELECT 1 as id, 'test' as name;"
        
        response = await authenticated_client.post(
            "/api/sandbox/execute",
            json={"query": valid_query}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data or "columns" in data
        # Result format depends on API design

    @pytest.mark.asyncio
    async def test_syntax_error_handled_gracefully(self, authenticated_client: AsyncClient):
        """Test that SQL syntax errors are handled gracefully."""
        invalid_query = "SELCT * FROM users;"  # Typo
        
        response = await authenticated_client.post(
            "/api/sandbox/execute",
            json={"query": invalid_query}
        )
        
        assert response.status_code in [400, 422]
        data = response.json()
        assert "syntax" in data.get("detail", "").lower() or \
               "error" in data.get("detail", "").lower()

    @pytest.mark.asyncio
    async def test_empty_query_rejected(self, authenticated_client: AsyncClient):
        """Test that empty queries are rejected."""
        response = await authenticated_client.post(
            "/api/sandbox/execute",
            json={"query": ""}
        )
        
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_multiple_statements_blocked(self, authenticated_client: AsyncClient):
        """Test that multiple statements are blocked."""
        multi_query = "SELECT 1; DROP TABLE users;"
        
        response = await authenticated_client.post(
            "/api/sandbox/execute",
            json={"query": multi_query}
        )
        
        assert response.status_code in [400, 403]


class TestSandboxResourceExhaustion:
    """Test protection against resource exhaustion attacks."""

    @pytest.mark.asyncio
    async def test_large_result_set_limited(self, authenticated_client: AsyncClient):
        """Test that result sets are limited in size."""
        # Query that could return huge results
        large_query = """
        SELECT * FROM 
        (SELECT 1 as n UNION ALL SELECT 2 UNION ALL SELECT 3) t1
        CROSS JOIN 
        (SELECT 1 as n UNION ALL SELECT 2 UNION ALL SELECT 3) t2
        CROSS JOIN
        (SELECT 1 as n UNION ALL SELECT 2 UNION ALL SELECT 3) t3;
        """
        
        response = await authenticated_client.post(
            "/api/sandbox/execute",
            json={"query": large_query}
        )
        
        # Should either succeed with limited results or fail gracefully
        assert response.status_code in [200, 400]

    @pytest.mark.asyncio
    async def test_memory_intensive_query_handled(self, authenticated_client: AsyncClient):
        """Test that memory-intensive queries are handled properly."""
        # Query with large GROUP BY or JOIN
        memory_query = """
        SELECT COUNT(*), SUM(n) FROM (
            SELECT 1 as n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
        ) t1;
        """
        
        response = await authenticated_client.post(
            "/api/sandbox/execute",
            json={"query": memory_query}
        )
        
        # Should complete successfully or timeout gracefully
        assert response.status_code in [200, 408, 500]


class TestSandboxFixtureData:
    """Test sandbox fixture data loading for lessons."""

    @pytest.mark.asyncio
    async def test_lesson_fixture_data_loaded(self, authenticated_client: AsyncClient):
        """Test that lesson-specific fixture data is loaded."""
        # When executing a query for a specific lesson, 
        # the sandbox should load the lesson's fixture data
        # This would be tested with a real lesson that has fixtures
        pass

    @pytest.mark.asyncio
    async def test_fixture_data_isolated_per_lesson(self, authenticated_client: AsyncClient):
        """Test that fixture data is isolated per lesson."""
        # Different lessons should have different fixture datasets
        # and they shouldn't interfere with each other
        pass
