"""
Integration tests for query validation guard with sandbox executor.

Tests the pre-check integration and ensures invalid queries are rejected
with clear messages before execution.
"""

import pytest

from app.core.sandbox_config import SandboxConfig
from app.schemas.sandbox import SandboxStatus
from app.services.query_validator import QueryValidator, create_lesson_validator
from app.services.sandbox import (
    InMemorySandboxManager,
    MockQueryExecutor,
    MockSchemaManager,
    SandboxService,
)


@pytest.fixture
def sandbox_config() -> SandboxConfig:
    """Test sandbox configuration."""
    return SandboxConfig(
        enabled=True,
        mysql_admin_password="test_password",
        max_sandboxes_per_user=3,
        max_active_sandboxes=10,
        allowed_query_types=["SELECT", "INSERT", "UPDATE", "DELETE"],
    )


@pytest.fixture
def sandbox_service(sandbox_config: SandboxConfig) -> SandboxService:
    """Create sandbox service with all components."""
    return SandboxService(
        config=sandbox_config,
        sandbox_manager=InMemorySandboxManager(sandbox_config),
        schema_manager=MockSchemaManager(sandbox_config),
        query_executor=MockQueryExecutor(sandbox_config),
    )


class TestExecutorPreCheck:
    """Test that query validation happens before execution."""

    async def test_valid_query_executes(self, sandbox_service: SandboxService) -> None:
        """Valid queries should execute successfully."""
        sandbox = await sandbox_service.create_sandbox(user_id=1, lesson_id=1)

        result = await sandbox_service.execute_query(
            sandbox.sandbox_id,
            "SELECT * FROM employees WHERE department = 'Engineering'",
        )

        assert result.row_count >= 0
        assert isinstance(result.columns, list)

    async def test_blocked_query_rejected_before_execution(
        self, sandbox_service: SandboxService
    ) -> None:
        """Destructive queries should be rejected before execution."""
        sandbox = await sandbox_service.create_sandbox(user_id=1, lesson_id=1)

        with pytest.raises(ValueError) as exc_info:
            await sandbox_service.execute_query(sandbox.sandbox_id, "DROP TABLE employees")

        error_message = str(exc_info.value).lower()
        assert "invalid query" in error_message or "blocked" in error_message

    async def test_system_schema_access_rejected(
        self, sandbox_service: SandboxService
    ) -> None:
        """System schema access should be rejected."""
        sandbox = await sandbox_service.create_sandbox(user_id=1, lesson_id=1)

        with pytest.raises(ValueError) as exc_info:
            await sandbox_service.execute_query(
                sandbox.sandbox_id, "SELECT * FROM information_schema.tables"
            )

        assert "invalid query" in str(exc_info.value).lower()

    async def test_sql_injection_attempt_rejected(
        self, sandbox_service: SandboxService
    ) -> None:
        """SQL injection attempts should be rejected."""
        sandbox = await sandbox_service.create_sandbox(user_id=1, lesson_id=1)

        with pytest.raises(ValueError) as exc_info:
            await sandbox_service.execute_query(
                sandbox.sandbox_id,
                "SELECT * FROM users WHERE id = 1 UNION SELECT password FROM users",
            )

        assert "invalid query" in str(exc_info.value).lower()


class TestClearErrorMessages:
    """Test that validation errors provide clear, actionable messages."""

    async def test_drop_table_clear_message(self, sandbox_service: SandboxService) -> None:
        """DROP TABLE should have clear error message."""
        sandbox = await sandbox_service.create_sandbox(user_id=1, lesson_id=1)

        with pytest.raises(ValueError) as exc_info:
            await sandbox_service.execute_query(sandbox.sandbox_id, "DROP TABLE employees")

        error_msg = str(exc_info.value)
        # Should mention what's blocked
        assert "DROP" in error_msg or "blocked" in error_msg.lower()

    async def test_system_schema_clear_message(
        self, sandbox_service: SandboxService
    ) -> None:
        """System schema access should have clear error message."""
        sandbox = await sandbox_service.create_sandbox(user_id=1, lesson_id=1)

        with pytest.raises(ValueError) as exc_info:
            await sandbox_service.execute_query(
                sandbox.sandbox_id, "SELECT * FROM mysql.user"
            )

        error_msg = str(exc_info.value)
        assert "mysql" in error_msg.lower() or "system" in error_msg.lower()

    async def test_disallowed_query_type_clear_message(self) -> None:
        """Disallowed query types should have clear error message."""
        config = SandboxConfig(
            enabled=True,
            mysql_admin_password="test_password",
            allowed_query_types=["SELECT"],
        )
        service = SandboxService(
            config=config,
            sandbox_manager=InMemorySandboxManager(config),
            schema_manager=MockSchemaManager(config),
            query_executor=MockQueryExecutor(config),
        )

        sandbox = await service.create_sandbox(user_id=1, lesson_id=1)

        with pytest.raises(ValueError) as exc_info:
            await service.execute_query(
                sandbox.sandbox_id, "INSERT INTO users (name) VALUES ('test')"
            )

        error_msg = str(exc_info.value)
        assert "INSERT" in error_msg or "not allowed" in error_msg.lower()


class TestLessonSpecificValidation:
    """Test lesson-specific query restrictions."""

    async def test_basic_lesson_allows_select(self, sandbox_config: SandboxConfig) -> None:
        """Basic lessons should allow SELECT queries."""
        validator = create_lesson_validator(sandbox_config, lesson_id=1, allowed_types=["SELECT"])

        result = validator.validate("SELECT * FROM employees")
        assert result.is_valid is True

    async def test_basic_lesson_blocks_insert(self, sandbox_config: SandboxConfig) -> None:
        """Basic lessons should block INSERT queries."""
        validator = create_lesson_validator(sandbox_config, lesson_id=1, allowed_types=["SELECT"])

        result = validator.validate("INSERT INTO employees (name) VALUES ('test')", lesson_id=1)
        assert result.is_valid is False
        assert any("lesson" in error.lower() for error in result.errors)

    async def test_advanced_lesson_allows_dml(self, sandbox_config: SandboxConfig) -> None:
        """Advanced lessons should allow DML operations."""
        validator = create_lesson_validator(
            sandbox_config, lesson_id=10, allowed_types=["SELECT", "INSERT", "UPDATE", "DELETE"]
        )

        queries = [
            "SELECT * FROM employees",
            "INSERT INTO employees (name) VALUES ('test')",
            "UPDATE employees SET name = 'updated' WHERE id = 1",
            "DELETE FROM employees WHERE id = 1",
        ]

        for query in queries:
            result = validator.validate(query)
            assert result.is_valid is True, f"Query should be valid: {query}"


class TestBlockedCommandsPerModule:
    """Test blocked commands across different learning modules."""

    def test_module1_basic_select_allowed(self, sandbox_config: SandboxConfig) -> None:
        """Module 1 (SELECT basics) should allow SELECT."""
        validator = create_lesson_validator(sandbox_config, lesson_id=1, allowed_types=["SELECT"])

        queries = [
            "SELECT * FROM employees",
            "SELECT name, salary FROM employees WHERE department = 'IT'",
            "SELECT COUNT(*) FROM employees",
        ]

        for query in queries:
            result = validator.validate(query)
            assert result.is_valid is True

    def test_module1_insert_blocked(self, sandbox_config: SandboxConfig) -> None:
        """Module 1 should block INSERT."""
        validator = create_lesson_validator(sandbox_config, lesson_id=1, allowed_types=["SELECT"])

        result = validator.validate("INSERT INTO employees (name) VALUES ('test')")
        assert result.is_valid is False

    def test_module2_insert_allowed(self, sandbox_config: SandboxConfig) -> None:
        """Module 2 (INSERT basics) should allow INSERT."""
        validator = create_lesson_validator(
            sandbox_config, lesson_id=5, allowed_types=["SELECT", "INSERT"]
        )

        result = validator.validate("INSERT INTO employees (name) VALUES ('test')")
        assert result.is_valid is True

    def test_module3_update_allowed(self, sandbox_config: SandboxConfig) -> None:
        """Module 3 (UPDATE basics) should allow UPDATE."""
        validator = create_lesson_validator(
            sandbox_config, lesson_id=10, allowed_types=["SELECT", "UPDATE"]
        )

        result = validator.validate("UPDATE employees SET salary = 60000 WHERE id = 1")
        assert result.is_valid is True

    def test_module4_delete_allowed(self, sandbox_config: SandboxConfig) -> None:
        """Module 4 (DELETE basics) should allow DELETE."""
        validator = create_lesson_validator(
            sandbox_config, lesson_id=15, allowed_types=["SELECT", "DELETE"]
        )

        result = validator.validate("DELETE FROM employees WHERE id = 1")
        assert result.is_valid is True


class TestAllowedExamplesPerModule:
    """Specific examples of allowed queries per module."""

    def test_module1_lesson1_allowed_queries(self, sandbox_config: SandboxConfig) -> None:
        """Module 1, Lesson 1: Basic SELECT queries."""
        validator = create_lesson_validator(sandbox_config, lesson_id=1, allowed_types=["SELECT"])

        allowed = [
            "SELECT * FROM employees",
            "SELECT name FROM employees",
            "SELECT name, salary FROM employees",
        ]

        for query in allowed:
            result = validator.validate(query, lesson_id=1)
            assert result.is_valid is True, f"Should allow: {query}"

    def test_module1_lesson2_allowed_queries(self, sandbox_config: SandboxConfig) -> None:
        """Module 1, Lesson 2: SELECT with WHERE."""
        validator = create_lesson_validator(sandbox_config, lesson_id=2, allowed_types=["SELECT"])

        allowed = [
            "SELECT * FROM employees WHERE department = 'IT'",
            "SELECT name FROM employees WHERE salary > 50000",
            "SELECT * FROM employees WHERE hire_date > '2020-01-01'",
        ]

        for query in allowed:
            result = validator.validate(query, lesson_id=2)
            assert result.is_valid is True, f"Should allow: {query}"

    def test_module2_lesson5_allowed_queries(self, sandbox_config: SandboxConfig) -> None:
        """Module 2, Lesson 5: INSERT basics."""
        validator = create_lesson_validator(
            sandbox_config, lesson_id=5, allowed_types=["SELECT", "INSERT"]
        )

        allowed = [
            "INSERT INTO employees (name, department) VALUES ('John Doe', 'IT')",
            "INSERT INTO employees (name) VALUES ('Jane Smith')",
            "SELECT * FROM employees",
        ]

        for query in allowed:
            result = validator.validate(query, lesson_id=5)
            assert result.is_valid is True, f"Should allow: {query}"


class TestBlockedExamplesPerModule:
    """Specific examples of blocked queries per module."""

    def test_module1_blocked_queries(self, sandbox_config: SandboxConfig) -> None:
        """Module 1 should block all non-SELECT queries."""
        validator = create_lesson_validator(sandbox_config, lesson_id=1, allowed_types=["SELECT"])

        blocked = [
            "INSERT INTO employees (name) VALUES ('test')",
            "UPDATE employees SET salary = 50000",
            "DELETE FROM employees WHERE id = 1",
            "DROP TABLE employees",
            "TRUNCATE TABLE employees",
        ]

        for query in blocked:
            result = validator.validate(query, lesson_id=1)
            assert result.is_valid is False, f"Should block: {query}"

    def test_all_modules_block_destructive(self, sandbox_config: SandboxConfig) -> None:
        """All modules should block destructive operations."""
        # Test across different lesson configs
        lesson_configs = [
            (1, ["SELECT"]),
            (5, ["SELECT", "INSERT"]),
            (10, ["SELECT", "INSERT", "UPDATE"]),
            (15, ["SELECT", "INSERT", "UPDATE", "DELETE"]),
        ]

        blocked = [
            "DROP TABLE employees",
            "DROP DATABASE test",
            "TRUNCATE TABLE employees",
            "ALTER TABLE employees ADD COLUMN test INT",
            "CREATE DATABASE newdb",
        ]

        for lesson_id, allowed_types in lesson_configs:
            validator = create_lesson_validator(
                sandbox_config, lesson_id=lesson_id, allowed_types=allowed_types
            )

            for query in blocked:
                result = validator.validate(query, lesson_id=lesson_id)
                assert result.is_valid is False, (
                    f"Lesson {lesson_id} should block: {query}"
                )

    def test_all_modules_block_system_schemas(self, sandbox_config: SandboxConfig) -> None:
        """All modules should block system schema access."""
        blocked_queries = [
            "SELECT * FROM information_schema.tables",
            "SELECT * FROM mysql.user",
            "SELECT * FROM performance_schema.events",
            "SELECT * FROM sys.schema_table_statistics",
        ]

        # Test with different lesson types
        for lesson_id in [1, 5, 10, 15]:
            validator = create_lesson_validator(
                sandbox_config, lesson_id=lesson_id, allowed_types=["SELECT"]
            )

            for query in blocked_queries:
                result = validator.validate(query, lesson_id=lesson_id)
                assert result.is_valid is False, (
                    f"Lesson {lesson_id} should block: {query}"
                )


class TestValidatorIntegrationWithMockExecutor:
    """Test validator integration with MockQueryExecutor."""

    async def test_executor_uses_validator(self, sandbox_config: SandboxConfig) -> None:
        """Executor should use validator for pre-check."""
        executor = MockQueryExecutor(sandbox_config)
        manager = InMemorySandboxManager(sandbox_config)

        sandbox = await manager.create_sandbox(user_id=1, lesson_id=1)
        sandbox.status = SandboxStatus.ACTIVE

        # Valid query should execute
        result = await executor.execute_query(sandbox, "SELECT * FROM employees")
        assert result.row_count >= 0

        # Invalid query should raise error
        with pytest.raises(ValueError) as exc_info:
            await executor.execute_query(sandbox, "DROP TABLE employees")

        assert "invalid query" in str(exc_info.value).lower()

    async def test_validator_called_before_execution(
        self, sandbox_config: SandboxConfig
    ) -> None:
        """Validation should happen before any execution logic."""
        executor = MockQueryExecutor(sandbox_config)

        # Test validate_query method directly
        valid_result = await executor.validate_query("SELECT * FROM users")
        assert valid_result.is_valid is True

        invalid_result = await executor.validate_query("DROP TABLE users")
        assert invalid_result.is_valid is False
        assert len(invalid_result.errors) > 0
