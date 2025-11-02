"""
Integration tests for sandbox SQL executor with timeout, diffing, and security tests.
"""

import asyncio
from typing import Any

import pytest

from app.core.sandbox_config import SandboxConfig
from app.schemas.sandbox import QueryExecuteResponse
from app.services.query_executor import MySQLQueryExecutor
from app.services.sandbox import InMemorySandboxManager, Sandbox, SandboxStatus
from app.services.schema_manager import MySQLSchemaManager


class TestQueryExecutorTimeout:
    """Test timeout enforcement for query execution."""

    @pytest.fixture
    def config(self) -> SandboxConfig:
        return SandboxConfig(
            enabled=True,
            query_timeout_seconds=2,
            mysql_admin_password="test_password",
        )

    @pytest.fixture
    def executor(self, config: SandboxConfig) -> MySQLQueryExecutor:
        return MySQLQueryExecutor(config)

    @pytest.fixture
    def mock_sandbox(self) -> Sandbox:
        from datetime import UTC, datetime, timedelta

        now = datetime.now(UTC)
        return Sandbox(
            sandbox_id="test_1_1_12345",
            user_id=1,
            lesson_id=1,
            schema_name="sandbox_user_1_12345",
            status=SandboxStatus.ACTIVE,
            created_at=now,
            expires_at=now + timedelta(hours=1),
            last_accessed_at=now,
        )

    @pytest.mark.asyncio
    async def test_timeout_enforcement(self, executor: MySQLQueryExecutor, mock_sandbox: Sandbox):
        """Test that queries timing out raise TimeoutError."""

        # Create a mock query that would take too long
        async def slow_query():
            await asyncio.sleep(3)  # Longer than timeout
            return QueryExecuteResponse(columns=[], rows=[], row_count=0, execution_time=3.0)

        # Monkey patch the executor's internal method
        original_method = executor._execute_with_connection
        executor._execute_with_connection = lambda s, q, qt: slow_query()

        try:
            with pytest.raises(TimeoutError, match="exceeded timeout"):
                await executor.execute_query(mock_sandbox, "SELECT * FROM test", timeout=1.0)
        finally:
            executor._execute_with_connection = original_method

    @pytest.mark.asyncio
    async def test_custom_timeout(self, executor: MySQLQueryExecutor, mock_sandbox: Sandbox):
        """Test that custom timeout overrides default."""
        # This should complete quickly
        query = "SELECT 1"

        # Mock the execution
        async def quick_query(s, q, qt):
            return QueryExecuteResponse(
                columns=["1"], rows=[[1]], row_count=1, execution_time=0.001
            )

        executor._execute_with_connection = quick_query

        # Should not timeout with generous timeout
        result = await executor.execute_query(mock_sandbox, query, timeout=10.0)
        assert result.row_count == 1


class TestResultComparison:
    """Test order-insensitive result comparison."""

    @pytest.fixture
    def executor(self) -> MySQLQueryExecutor:
        config = SandboxConfig(enabled=True, mysql_admin_password="test_password")
        return MySQLQueryExecutor(config)

    def test_exact_match(self, executor: MySQLQueryExecutor):
        """Test exact match between user and expected results."""
        user_result = QueryExecuteResponse(
            columns=["id", "name"],
            rows=[[1, "Alice"], [2, "Bob"]],
            row_count=2,
            execution_time=0.1,
        )

        expected = {"columns": ["id", "name"], "rows": [[1, "Alice"], [2, "Bob"]]}

        matches, differences = executor.compare_results(user_result, expected, ordered=True)
        assert matches is True
        assert len(differences) == 0

    def test_order_insensitive_match(self, executor: MySQLQueryExecutor):
        """Test order-insensitive comparison."""
        user_result = QueryExecuteResponse(
            columns=["id", "name"],
            rows=[[2, "Bob"], [1, "Alice"]],  # Different order
            row_count=2,
            execution_time=0.1,
        )

        expected = {"columns": ["id", "name"], "rows": [[1, "Alice"], [2, "Bob"]]}

        matches, differences = executor.compare_results(user_result, expected, ordered=False)
        assert matches is True
        assert len(differences) == 0

    def test_order_sensitive_mismatch(self, executor: MySQLQueryExecutor):
        """Test that ordered comparison detects order differences."""
        user_result = QueryExecuteResponse(
            columns=["id", "name"],
            rows=[[2, "Bob"], [1, "Alice"]],  # Different order
            row_count=2,
            execution_time=0.1,
        )

        expected = {"columns": ["id", "name"], "rows": [[1, "Alice"], [2, "Bob"]]}

        matches, differences = executor.compare_results(user_result, expected, ordered=True)
        assert matches is False
        assert len(differences) > 0
        assert any("mismatch" in d.lower() for d in differences)

    def test_row_count_mismatch(self, executor: MySQLQueryExecutor):
        """Test detection of row count mismatch."""
        user_result = QueryExecuteResponse(
            columns=["id", "name"],
            rows=[[1, "Alice"]],  # Missing a row
            row_count=1,
            execution_time=0.1,
        )

        expected = {"columns": ["id", "name"], "rows": [[1, "Alice"], [2, "Bob"]]}

        matches, differences = executor.compare_results(user_result, expected, ordered=False)
        assert matches is False
        assert any("Row count mismatch" in d for d in differences)

    def test_column_mismatch(self, executor: MySQLQueryExecutor):
        """Test detection of column mismatch."""
        user_result = QueryExecuteResponse(
            columns=["id", "email"],  # Wrong column
            rows=[[1, "alice@example.com"]],
            row_count=1,
            execution_time=0.1,
        )

        expected = {"columns": ["id", "name"], "rows": [[1, "Alice"]]}

        matches, differences = executor.compare_results(user_result, expected, ordered=False)
        assert matches is False
        assert any("Column mismatch" in d for d in differences)

    def test_missing_rows(self, executor: MySQLQueryExecutor):
        """Test detection of missing rows."""
        user_result = QueryExecuteResponse(
            columns=["id", "name"],
            rows=[[1, "Alice"]],
            row_count=1,
            execution_time=0.1,
        )

        expected = {
            "columns": ["id", "name"],
            "rows": [[1, "Alice"], [2, "Bob"], [3, "Charlie"]],
        }

        matches, differences = executor.compare_results(user_result, expected, ordered=False)
        assert matches is False
        assert any("Missing rows" in d for d in differences)

    def test_extra_rows(self, executor: MySQLQueryExecutor):
        """Test detection of extra rows."""
        user_result = QueryExecuteResponse(
            columns=["id", "name"],
            rows=[[1, "Alice"], [2, "Bob"], [3, "Charlie"]],
            row_count=3,
            execution_time=0.1,
        )

        expected = {"columns": ["id", "name"], "rows": [[1, "Alice"], [2, "Bob"]]}

        matches, differences = executor.compare_results(user_result, expected, ordered=False)
        assert matches is False
        assert any("Extra rows" in d for d in differences)

    def test_value_normalization(self, executor: MySQLQueryExecutor):
        """Test that values are normalized correctly for comparison."""
        user_result = QueryExecuteResponse(
            columns=["id", "price"],
            rows=[[1, 10.123456789]],  # Many decimal places
            row_count=1,
            execution_time=0.1,
        )

        expected = {"columns": ["id", "price"], "rows": [[1, 10.123457]]}  # Rounded

        matches, differences = executor.compare_results(user_result, expected, ordered=False)
        assert matches is True  # Should match after normalization


class TestErrorSanitization:
    """Test error message sanitization."""

    @pytest.fixture
    def executor(self) -> MySQLQueryExecutor:
        config = SandboxConfig(enabled=True, mysql_admin_password="test_password")
        return MySQLQueryExecutor(config)

    def test_sanitize_file_paths(self, executor: MySQLQueryExecutor):
        """Test that file paths are sanitized."""
        error = "Error in /var/lib/mysql/data/table.frm"
        sanitized = executor._sanitize_error(error)
        assert "/var/lib/mysql" not in sanitized
        assert "[path]" in sanitized

    def test_sanitize_ip_addresses(self, executor: MySQLQueryExecutor):
        """Test that IP addresses are sanitized."""
        error = "Connection refused to 192.168.1.100"
        sanitized = executor._sanitize_error(error)
        assert "192.168.1.100" not in sanitized
        assert "[ip]" in sanitized

    def test_sanitize_port_numbers(self, executor: MySQLQueryExecutor):
        """Test that port numbers are sanitized."""
        error = "Connection to host:3306 failed"
        sanitized = executor._sanitize_error(error)
        assert "3306" not in sanitized
        assert "[port]" in sanitized

    def test_sanitize_schema_names(self, executor: MySQLQueryExecutor):
        """Test that sandbox schema names are sanitized."""
        error = "Access denied to sandbox_user_123_456789"
        sanitized = executor._sanitize_error(error)
        assert "sandbox_user_123_456789" not in sanitized
        assert "[schema]" in sanitized

    def test_length_limit(self, executor: MySQLQueryExecutor):
        """Test that long error messages are truncated."""
        error = "A" * 1000
        sanitized = executor._sanitize_error(error)
        assert len(sanitized) <= 503  # 500 + "..."


class TestMaliciousQueryBlocking:
    """Test that malicious queries are blocked."""

    @pytest.fixture
    def config(self) -> SandboxConfig:
        return SandboxConfig(enabled=True, mysql_admin_password="test_password")

    @pytest.fixture
    def executor(self, config: SandboxConfig) -> MySQLQueryExecutor:
        return MySQLQueryExecutor(config)

    @pytest.mark.asyncio
    async def test_block_drop_table(self, executor: MySQLQueryExecutor):
        """Test that DROP TABLE is blocked."""
        query = "DROP TABLE users"
        validation = await executor.validate_query(query)
        assert validation.is_valid is False
        assert any("blocked pattern" in e.lower() for e in validation.errors)

    @pytest.mark.asyncio
    async def test_block_truncate(self, executor: MySQLQueryExecutor):
        """Test that TRUNCATE is blocked."""
        query = "TRUNCATE TABLE users"
        validation = await executor.validate_query(query)
        assert validation.is_valid is False
        assert any("blocked pattern" in e.lower() for e in validation.errors)

    @pytest.mark.asyncio
    async def test_block_alter_table(self, executor: MySQLQueryExecutor):
        """Test that ALTER TABLE is blocked."""
        query = "ALTER TABLE users ADD COLUMN evil VARCHAR(100)"
        validation = await executor.validate_query(query)
        assert validation.is_valid is False
        assert any("blocked pattern" in e.lower() for e in validation.errors)

    @pytest.mark.asyncio
    async def test_block_create_database(self, executor: MySQLQueryExecutor):
        """Test that CREATE DATABASE is blocked."""
        query = "CREATE DATABASE evil_db"
        validation = await executor.validate_query(query)
        assert validation.is_valid is False
        assert any("blocked pattern" in e.lower() for e in validation.errors)

    @pytest.mark.asyncio
    async def test_block_grant(self, executor: MySQLQueryExecutor):
        """Test that GRANT is blocked."""
        query = "GRANT ALL PRIVILEGES ON *.* TO 'user'@'host'"
        validation = await executor.validate_query(query)
        assert validation.is_valid is False
        assert any("blocked pattern" in e.lower() for e in validation.errors)

    @pytest.mark.asyncio
    async def test_block_system_schema_access(self, executor: MySQLQueryExecutor):
        """Test that access to system schemas is blocked."""
        queries = [
            "SELECT * FROM mysql.user",
            "SELECT * FROM information_schema.tables",
            "SELECT * FROM performance_schema.events",
        ]

        for query in queries:
            validation = await executor.validate_query(query)
            assert validation.is_valid is False
            assert any("blocked pattern" in e.lower() for e in validation.errors)

    @pytest.mark.asyncio
    async def test_allow_safe_select(self, executor: MySQLQueryExecutor):
        """Test that safe SELECT queries are allowed."""
        query = "SELECT * FROM employees WHERE department = 'Engineering'"
        validation = await executor.validate_query(query)
        assert validation.is_valid is True

    @pytest.mark.asyncio
    async def test_allow_safe_insert(self, executor: MySQLQueryExecutor):
        """Test that safe INSERT queries are allowed."""
        query = "INSERT INTO employees (name, department) VALUES ('John', 'Engineering')"
        validation = await executor.validate_query(query)
        assert validation.is_valid is True

    @pytest.mark.asyncio
    async def test_allow_safe_update(self, executor: MySQLQueryExecutor):
        """Test that safe UPDATE queries are allowed."""
        query = "UPDATE employees SET salary = 80000 WHERE id = 1"
        validation = await executor.validate_query(query)
        assert validation.is_valid is True

    @pytest.mark.asyncio
    async def test_allow_safe_delete(self, executor: MySQLQueryExecutor):
        """Test that safe DELETE queries are allowed."""
        query = "DELETE FROM employees WHERE id = 999"
        validation = await executor.validate_query(query)
        assert validation.is_valid is True

    @pytest.mark.asyncio
    async def test_block_sql_injection_attempt(self, executor: MySQLQueryExecutor):
        """Test that SQL injection patterns are detected."""
        # These might not all be blocked depending on config, but DROP should be
        injection_queries = [
            "SELECT * FROM users; DROP TABLE users; --",
            "SELECT * FROM users WHERE id = 1 OR 1=1; DROP TABLE users",
        ]

        for query in injection_queries:
            validation = await executor.validate_query(query)
            # At minimum, the DROP should be blocked
            if "DROP" in query:
                assert validation.is_valid is False


class TestSchemaManager:
    """Test schema manager operations."""

    @pytest.fixture
    def config(self) -> SandboxConfig:
        return SandboxConfig(enabled=True, mysql_admin_password="test_password")

    @pytest.fixture
    def schema_manager(self, config: SandboxConfig) -> MySQLSchemaManager:
        return MySQLSchemaManager(config)

    def test_fixture_data_available(self, schema_manager: MySQLSchemaManager):
        """Test that fixture data is available for lessons."""
        fixture = asyncio.run(schema_manager._get_lesson_fixture(1))
        assert fixture is not None
        assert "CREATE TABLE" in fixture
        assert "INSERT INTO" in fixture

    def test_sql_statement_splitting(self, schema_manager: MySQLSchemaManager):
        """Test that SQL is properly split into statements."""
        sql = """
        CREATE TABLE test (id INT);
        INSERT INTO test VALUES (1);
        INSERT INTO test VALUES (2);
        """

        statements = schema_manager._split_sql_statements(sql)
        assert len(statements) >= 2  # At least CREATE and INSERT

    def test_comment_filtering(self, schema_manager: MySQLSchemaManager):
        """Test that SQL comments are filtered out."""
        sql = """
        -- This is a comment
        CREATE TABLE test (id INT);
        -- Another comment
        INSERT INTO test VALUES (1);
        """

        statements = schema_manager._split_sql_statements(sql)
        # Comments should be filtered
        for stmt in statements:
            assert not stmt.strip().startswith("--")


class TestIntegrationWorkflow:
    """Integration tests for complete sandbox workflow."""

    @pytest.fixture
    def config(self) -> SandboxConfig:
        return SandboxConfig(
            enabled=True,
            mysql_admin_password="test_password",
            query_timeout_seconds=5,
            max_result_rows=100,
        )

    @pytest.fixture
    def sandbox_manager(self, config: SandboxConfig) -> InMemorySandboxManager:
        return InMemorySandboxManager(config)

    @pytest.fixture
    def executor(self, config: SandboxConfig) -> MySQLQueryExecutor:
        return MySQLQueryExecutor(config)

    @pytest.mark.asyncio
    async def test_complete_workflow(
        self, sandbox_manager: InMemorySandboxManager, executor: MySQLQueryExecutor
    ):
        """Test complete sandbox workflow from creation to query execution."""
        # Create sandbox
        sandbox = await sandbox_manager.create_sandbox(user_id=1, lesson_id=1)
        assert sandbox.status == SandboxStatus.CREATING

        # Activate sandbox
        sandbox.status = SandboxStatus.ACTIVE

        # Validate query
        query = "SELECT * FROM employees WHERE department = 'Engineering'"
        validation = await executor.validate_query(query)
        assert validation.is_valid is True

        # Update access
        await sandbox_manager.update_sandbox_access(sandbox.sandbox_id)
        assert sandbox.query_count == 1

        # Cleanup
        await sandbox_manager.destroy_sandbox(sandbox.sandbox_id)
        destroyed = await sandbox_manager.get_sandbox(sandbox.sandbox_id)
        assert destroyed is None

    @pytest.mark.asyncio
    async def test_max_sandboxes_per_user(self, sandbox_manager: InMemorySandboxManager):
        """Test that user cannot exceed max sandboxes limit."""
        # Create max allowed sandboxes
        for i in range(3):  # default max_sandboxes_per_user is 3
            sandbox = await sandbox_manager.create_sandbox(user_id=1, lesson_id=i + 1)
            sandbox.status = SandboxStatus.ACTIVE

        # Try to create one more - should fail
        with pytest.raises(ValueError, match="maximum"):
            await sandbox_manager.create_sandbox(user_id=1, lesson_id=99)

    @pytest.mark.asyncio
    async def test_expired_sandbox_cleanup(self, sandbox_manager: InMemorySandboxManager):
        """Test that expired sandboxes are cleaned up."""
        from datetime import UTC, datetime, timedelta

        # Create sandbox
        sandbox = await sandbox_manager.create_sandbox(user_id=1, lesson_id=1)
        sandbox.status = SandboxStatus.ACTIVE

        # Manually expire it
        sandbox.expires_at = datetime.now(UTC) - timedelta(hours=1)

        # Run cleanup
        result = await sandbox_manager.cleanup_expired_sandboxes()
        assert result.cleaned_count == 1
        assert sandbox.sandbox_id in result.cleaned_sandbox_ids
