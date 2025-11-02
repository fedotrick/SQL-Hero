"""
Comprehensive tests for query validation guard.

Tests cover:
- Allowed queries per lesson type
- Blocked destructive commands
- System table protection
- SQL injection prevention
- Lesson-specific query restrictions
- Clear error messages
"""

import pytest

from app.core.sandbox_config import SandboxConfig
from app.services.query_validator import (
    LessonQueryPolicy,
    QueryValidator,
    create_lesson_validator,
    create_module_validator,
)


@pytest.fixture
def default_config() -> SandboxConfig:
    """Default sandbox configuration for testing."""
    return SandboxConfig(
        enabled=True,
        mysql_admin_password="test_password",
        allowed_query_types=["SELECT", "INSERT", "UPDATE", "DELETE"],
    )


@pytest.fixture
def select_only_config() -> SandboxConfig:
    """Configuration allowing only SELECT queries."""
    return SandboxConfig(
        enabled=True,
        mysql_admin_password="test_password",
        allowed_query_types=["SELECT"],
    )


@pytest.fixture
def validator(default_config: SandboxConfig) -> QueryValidator:
    """Default query validator."""
    return QueryValidator(default_config)


class TestBasicValidation:
    """Test basic query validation functionality."""

    def test_empty_query(self, validator: QueryValidator) -> None:
        result = validator.validate("")
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "empty" in result.errors[0].lower()

    def test_whitespace_only_query(self, validator: QueryValidator) -> None:
        result = validator.validate("   \n\t   ")
        assert result.is_valid is False
        assert "empty" in result.errors[0].lower()


class TestAllowedQueries:
    """Test queries that should be allowed."""

    def test_simple_select(self, validator: QueryValidator) -> None:
        result = validator.validate("SELECT * FROM employees")
        assert result.is_valid is True
        assert result.query_type == "SELECT"
        assert len(result.errors) == 0

    def test_select_with_where(self, validator: QueryValidator) -> None:
        result = validator.validate("SELECT name, salary FROM employees WHERE id = 1")
        assert result.is_valid is True
        assert result.query_type == "SELECT"

    def test_select_with_join(self, validator: QueryValidator) -> None:
        query = """
            SELECT e.name, d.department_name
            FROM employees e
            JOIN departments d ON e.department_id = d.id
        """
        result = validator.validate(query)
        assert result.is_valid is True
        assert result.query_type == "SELECT"

    def test_select_with_subquery(self, validator: QueryValidator) -> None:
        query = """
            SELECT name FROM employees
            WHERE salary > (SELECT AVG(salary) FROM employees)
        """
        result = validator.validate(query)
        assert result.is_valid is True
        assert result.query_type == "SELECT"

    def test_select_with_cte(self, validator: QueryValidator) -> None:
        query = """
            WITH high_earners AS (
                SELECT * FROM employees WHERE salary > 100000
            )
            SELECT * FROM high_earners
        """
        result = validator.validate(query)
        assert result.is_valid is True
        assert result.query_type == "SELECT"

    def test_insert_query(self, validator: QueryValidator) -> None:
        result = validator.validate("INSERT INTO users (name) VALUES ('John')")
        assert result.is_valid is True
        assert result.query_type == "INSERT"

    def test_update_query_with_where(self, validator: QueryValidator) -> None:
        result = validator.validate("UPDATE users SET name = 'Jane' WHERE id = 1")
        assert result.is_valid is True
        assert result.query_type == "UPDATE"

    def test_delete_query_with_where(self, validator: QueryValidator) -> None:
        result = validator.validate("DELETE FROM users WHERE id = 1")
        assert result.is_valid is True
        assert result.query_type == "DELETE"


class TestBlockedDestructiveCommands:
    """Test that destructive commands are properly blocked."""

    def test_drop_table(self, validator: QueryValidator) -> None:
        result = validator.validate("DROP TABLE users")
        assert result.is_valid is False
        assert any("blocked operation" in error.lower() for error in result.errors)
        assert "DROP" in result.errors[0]

    def test_drop_database(self, validator: QueryValidator) -> None:
        result = validator.validate("DROP DATABASE mydb")
        assert result.is_valid is False
        assert any("blocked" in error.lower() for error in result.errors)

    def test_create_database(self, validator: QueryValidator) -> None:
        result = validator.validate("CREATE DATABASE newdb")
        assert result.is_valid is False
        assert any("blocked operation" in error.lower() for error in result.errors)

    def test_create_schema(self, validator: QueryValidator) -> None:
        result = validator.validate("CREATE SCHEMA newschema")
        assert result.is_valid is False
        assert any("blocked" in error.lower() for error in result.errors)

    def test_alter_table(self, validator: QueryValidator) -> None:
        result = validator.validate("ALTER TABLE users ADD COLUMN age INT")
        assert result.is_valid is False
        assert any("blocked operation" in error.lower() for error in result.errors)

    def test_truncate_table(self, validator: QueryValidator) -> None:
        result = validator.validate("TRUNCATE TABLE users")
        assert result.is_valid is False
        assert any("blocked operation" in error.lower() for error in result.errors)

    def test_grant_privileges(self, validator: QueryValidator) -> None:
        result = validator.validate("GRANT ALL ON *.* TO 'user'@'localhost'")
        assert result.is_valid is False
        assert any("blocked" in error.lower() for error in result.errors)

    def test_revoke_privileges(self, validator: QueryValidator) -> None:
        result = validator.validate("REVOKE ALL ON *.* FROM 'user'@'localhost'")
        assert result.is_valid is False
        assert any("blocked" in error.lower() for error in result.errors)


class TestSystemSchemaProtection:
    """Test that system schemas are protected from access."""

    def test_information_schema_blocked(self, validator: QueryValidator) -> None:
        result = validator.validate("SELECT * FROM information_schema.tables")
        assert result.is_valid is False
        assert any("system schema" in error.lower() for error in result.errors)
        assert "information_schema" in result.errors[0]

    def test_mysql_schema_blocked(self, validator: QueryValidator) -> None:
        result = validator.validate("SELECT * FROM mysql.user")
        assert result.is_valid is False
        assert any("system schema" in error.lower() for error in result.errors)
        assert "mysql" in result.errors[0]

    def test_performance_schema_blocked(self, validator: QueryValidator) -> None:
        result = validator.validate("SELECT * FROM performance_schema.events")
        assert result.is_valid is False
        assert any("system schema" in error.lower() for error in result.errors)

    def test_sys_schema_blocked(self, validator: QueryValidator) -> None:
        result = validator.validate("SELECT * FROM sys.schema_table_statistics")
        assert result.is_valid is False
        assert any("system schema" in error.lower() for error in result.errors)


class TestSQLInjectionPrevention:
    """Test that SQL injection attempts are detected and blocked."""

    def test_union_select_injection(self, validator: QueryValidator) -> None:
        result = validator.validate(
            "SELECT * FROM users WHERE id = 1 UNION SELECT password FROM users"
        )
        assert result.is_valid is False
        assert any("dangerous pattern" in error.lower() for error in result.errors)

    def test_stacked_queries(self, validator: QueryValidator) -> None:
        result = validator.validate("SELECT * FROM users; DROP TABLE users;")
        assert result.is_valid is False
        # Should catch either stacked queries or DROP
        assert len(result.errors) >= 1

    def test_comment_bypass_attempt(self, validator: QueryValidator) -> None:
        result = validator.validate("SELECT * FROM users WHERE 1=1 --")
        assert result.is_valid is False
        assert any("dangerous pattern" in error.lower() for error in result.errors)

    def test_system_variable_access(self, validator: QueryValidator) -> None:
        result = validator.validate("SELECT @@version")
        assert result.is_valid is False
        assert any("dangerous pattern" in error.lower() for error in result.errors)

    def test_outfile_injection(self, validator: QueryValidator) -> None:
        result = validator.validate("SELECT * FROM users INTO OUTFILE '/tmp/data.txt'")
        assert result.is_valid is False
        assert any("dangerous pattern" in error.lower() for error in result.errors)

    def test_load_data_blocked(self, validator: QueryValidator) -> None:
        result = validator.validate("LOAD DATA INFILE '/tmp/data.txt' INTO TABLE users")
        assert result.is_valid is False
        assert any("dangerous pattern" in error.lower() for error in result.errors)

    def test_load_file_function(self, validator: QueryValidator) -> None:
        result = validator.validate("SELECT LOAD_FILE('/etc/passwd')")
        assert result.is_valid is False
        assert any("dangerous pattern" in error.lower() for error in result.errors)


class TestQueryTypeRestrictions:
    """Test query type restrictions work correctly."""

    def test_allowed_query_type(self, validator: QueryValidator) -> None:
        result = validator.validate("SELECT * FROM users")
        assert result.is_valid is True
        assert result.query_type == "SELECT"

    def test_disallowed_query_type_select_only(self, select_only_config: SandboxConfig) -> None:
        validator = QueryValidator(select_only_config)
        result = validator.validate("INSERT INTO users (name) VALUES ('John')")
        assert result.is_valid is False
        assert any("not allowed" in error.lower() for error in result.errors)
        assert "INSERT" in result.errors[0]

    def test_error_message_includes_allowed_types(self, select_only_config: SandboxConfig) -> None:
        validator = QueryValidator(select_only_config)
        result = validator.validate("UPDATE users SET name = 'Jane'")
        assert result.is_valid is False
        assert "SELECT" in result.errors[0]  # Should mention allowed type


class TestLessonSpecificPolicies:
    """Test lesson-specific query restrictions."""

    def test_lesson_policy_select_only(self, default_config: SandboxConfig) -> None:
        policy = LessonQueryPolicy(lesson_id=1, allowed_query_types=["SELECT"])
        validator = QueryValidator(default_config, policy)

        result = validator.validate("INSERT INTO users (name) VALUES ('John')", lesson_id=1)
        assert result.is_valid is False
        assert "lesson" in result.errors[0].lower()
        assert "INSERT" in result.errors[0]

    def test_lesson_policy_allows_overrides(self, select_only_config: SandboxConfig) -> None:
        # Lesson allows INSERT even though global config is SELECT only
        policy = LessonQueryPolicy(lesson_id=5, allowed_query_types=["SELECT", "INSERT"])
        validator = QueryValidator(select_only_config, policy)

        result = validator.validate("INSERT INTO users (name) VALUES ('John')")
        assert result.is_valid is True

    def test_lesson_policy_falls_back_to_default(self, default_config: SandboxConfig) -> None:
        policy = LessonQueryPolicy(lesson_id=1)  # No override
        validator = QueryValidator(default_config, policy)

        result = validator.validate("SELECT * FROM users")
        assert result.is_valid is True

    def test_module_policy(self, default_config: SandboxConfig) -> None:
        policy = LessonQueryPolicy(module_id=3, allowed_query_types=["SELECT"])
        validator = QueryValidator(default_config, policy)

        result = validator.validate("DELETE FROM users WHERE id = 1")
        assert result.is_valid is False


class TestFactoryFunctions:
    """Test validator factory functions."""

    def test_create_lesson_validator(self, default_config: SandboxConfig) -> None:
        validator = create_lesson_validator(default_config, lesson_id=5, allowed_types=["SELECT"])

        result = validator.validate("SELECT * FROM users")
        assert result.is_valid is True

        result = validator.validate("INSERT INTO users (name) VALUES ('John')")
        assert result.is_valid is False

    def test_create_module_validator(self, default_config: SandboxConfig) -> None:
        validator = create_module_validator(
            default_config, module_id=2, allowed_types=["SELECT", "UPDATE"]
        )

        result = validator.validate("UPDATE users SET name = 'Jane' WHERE id = 1")
        assert result.is_valid is True

        result = validator.validate("DELETE FROM users WHERE id = 1")
        assert result.is_valid is False


class TestWarnings:
    """Test warning generation for potentially problematic queries."""

    def test_delete_without_where_warning(self, validator: QueryValidator) -> None:
        result = validator.validate("DELETE FROM users")
        assert result.is_valid is True  # Not invalid, just warned
        assert len(result.warnings) > 0
        assert any("without WHERE" in warning for warning in result.warnings)

    def test_update_without_where_warning(self, validator: QueryValidator) -> None:
        result = validator.validate("UPDATE users SET active = 1")
        assert result.is_valid is True  # Not invalid, just warned
        assert len(result.warnings) > 0
        assert any("without WHERE" in warning for warning in result.warnings)

    def test_long_query_warning(self, validator: QueryValidator) -> None:
        long_query = "SELECT * FROM users" + (" " * 5000)
        result = validator.validate(long_query)
        assert len(result.warnings) > 0
        assert any("long" in warning.lower() for warning in result.warnings)

    def test_many_selects_warning(self, validator: QueryValidator) -> None:
        # Create query with many SELECTs
        query = " UNION ".join(["SELECT * FROM users"] * 15)
        result = validator.validate(query)
        # Will likely be blocked for other reasons, but should have warning if valid
        if result.is_valid:
            assert any("many SELECT" in warning for warning in result.warnings)


class TestEdgeCases:
    """Test edge cases and corner scenarios."""

    def test_case_insensitive_detection(self, validator: QueryValidator) -> None:
        queries = [
            "select * from users",
            "SELECT * FROM users",
            "SeLeCt * FrOm users",
        ]
        for query in queries:
            result = validator.validate(query)
            assert result.is_valid is True
            assert result.query_type == "SELECT"

    def test_multiline_query(self, validator: QueryValidator) -> None:
        query = """
            SELECT
                id,
                name,
                email
            FROM
                users
            WHERE
                active = 1
        """
        result = validator.validate(query)
        assert result.is_valid is True
        assert result.query_type == "SELECT"

    def test_query_with_leading_comments_blocked(self, validator: QueryValidator) -> None:
        query = "/* comment */ SELECT * FROM users"
        result = validator.validate(query)
        # Comments are considered dangerous
        assert result.is_valid is False

    def test_blocked_pattern_in_string_literal(self, validator: QueryValidator) -> None:
        # This should be blocked because we use pattern matching
        # In production, a proper SQL parser would handle this correctly
        query = "SELECT * FROM users WHERE name = 'DROP'"
        result = validator.validate(query)
        # Current implementation will block this (overly conservative)
        assert result.is_valid is False

    def test_create_database_blocked_even_if_create_allowed(
        self, default_config: SandboxConfig
    ) -> None:
        # Even if we were to allow CREATE in the future, CREATE DATABASE should still be blocked
        # For now, use default config which doesn't allow CREATE anyway
        validator = QueryValidator(default_config)

        result = validator.validate("CREATE DATABASE testdb")
        assert result.is_valid is False
        assert any("blocked" in error.lower() for error in result.errors)


class TestPolicyDescription:
    """Test policy description generation."""

    def test_default_policy_description(self, validator: QueryValidator) -> None:
        description = validator.get_policy_description()
        assert "Default policy" in description
        assert "SELECT" in description

    def test_lesson_policy_description(self, default_config: SandboxConfig) -> None:
        policy = LessonQueryPolicy(lesson_id=5, allowed_query_types=["SELECT"])
        validator = QueryValidator(default_config, policy)

        description = validator.get_policy_description()
        assert "Lesson 5" in description
        assert "SELECT" in description

    def test_module_policy_description(self, default_config: SandboxConfig) -> None:
        policy = LessonQueryPolicy(module_id=3, allowed_query_types=["SELECT", "INSERT"])
        validator = QueryValidator(default_config, policy)

        description = validator.get_policy_description()
        assert "Module 3" in description
        assert "SELECT" in description
        assert "INSERT" in description


class TestMultipleErrors:
    """Test queries with multiple validation errors."""

    def test_multiple_violations(self, validator: QueryValidator) -> None:
        # Has both DROP and system schema access
        result = validator.validate("DROP TABLE information_schema.tables")
        assert result.is_valid is False
        assert len(result.errors) >= 2  # At least DROP and system schema

    def test_all_error_types(self, select_only_config: SandboxConfig) -> None:
        validator = QueryValidator(select_only_config)
        # Wrong type, has DROP, accesses system schema
        query = "DROP TABLE mysql.user"
        result = validator.validate(query)
        assert result.is_valid is False
        assert len(result.errors) >= 2  # Multiple violations
