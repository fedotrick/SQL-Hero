import pytest
from pydantic import ValidationError

from app.core.sandbox_config import SandboxConfig


class TestSandboxConfig:
    def test_default_config(self) -> None:
        config = SandboxConfig()

        assert config.enabled is False
        assert config.mysql_host == "localhost"
        assert config.mysql_port == 3306
        assert config.max_active_sandboxes == 1000
        assert config.max_sandboxes_per_user == 3
        assert config.idle_timeout_minutes == 30
        assert config.max_lifetime_hours == 4
        assert config.query_timeout_seconds == 30
        assert config.max_result_rows == 1000

    def test_enabled_requires_password(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            SandboxConfig(enabled=True, mysql_admin_password="")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("mysql_admin_password",)
        assert "required when sandbox is enabled" in errors[0]["msg"]

    def test_enabled_with_password(self) -> None:
        config = SandboxConfig(
            enabled=True,
            mysql_admin_password="secure_password123",
        )

        assert config.enabled is True
        assert config.mysql_admin_password == "secure_password123"

    def test_port_validation_too_low(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            SandboxConfig(mysql_port=0)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("mysql_port",) for error in errors)

    def test_port_validation_too_high(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            SandboxConfig(mysql_port=70000)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("mysql_port",) for error in errors)

    def test_port_validation_valid(self) -> None:
        config = SandboxConfig(mysql_port=3307)
        assert config.mysql_port == 3307

    def test_max_active_sandboxes_range(self) -> None:
        with pytest.raises(ValidationError):
            SandboxConfig(max_active_sandboxes=0)

        with pytest.raises(ValidationError):
            SandboxConfig(max_active_sandboxes=20000)

        config = SandboxConfig(max_active_sandboxes=500)
        assert config.max_active_sandboxes == 500

    def test_allowed_query_types_validation(self) -> None:
        config = SandboxConfig(allowed_query_types=["SELECT", "INSERT"])
        assert config.allowed_query_types == ["SELECT", "INSERT"]

    def test_allowed_query_types_normalized(self) -> None:
        config = SandboxConfig(allowed_query_types=["select", "insert"])
        assert config.allowed_query_types == ["SELECT", "INSERT"]

    def test_allowed_query_types_invalid(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            SandboxConfig(allowed_query_types=["SELECT", "DROP"])

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "Invalid query type: DROP" in errors[0]["msg"]

    def test_allowed_query_types_empty(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            SandboxConfig(allowed_query_types=[])

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "cannot be empty" in errors[0]["msg"]

    def test_blocked_patterns_empty(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            SandboxConfig(blocked_patterns=[])

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "cannot be empty" in errors[0]["msg"]

    def test_blocked_patterns_custom(self) -> None:
        custom_patterns = [r"\bDROP\b", r"\bTRUNCATE\b"]
        config = SandboxConfig(blocked_patterns=custom_patterns)
        assert config.blocked_patterns == custom_patterns

    def test_idle_timeout_exceeds_max_lifetime(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            SandboxConfig(
                idle_timeout_minutes=300,
                max_lifetime_hours=4,
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "idle_timeout_minutes" in str(errors[0]["msg"])
        assert "max_lifetime_hours" in str(errors[0]["msg"])

    def test_cleanup_interval_exceeds_idle_timeout(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            SandboxConfig(
                cleanup_interval_minutes=60,
                idle_timeout_minutes=30,
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert "cleanup_interval_minutes" in str(errors[0]["msg"])

    def test_valid_timeout_configuration(self) -> None:
        config = SandboxConfig(
            idle_timeout_minutes=30,
            max_lifetime_hours=4,
            cleanup_interval_minutes=5,
        )

        assert config.idle_timeout_minutes == 30
        assert config.max_lifetime_hours == 4
        assert config.cleanup_interval_minutes == 5

    def test_get_schema_name(self) -> None:
        config = SandboxConfig()
        schema_name = config.get_schema_name(user_id=123, timestamp=1704096000)

        assert schema_name == "sandbox_user_123_1704096000"
        assert config.is_sandbox_schema(schema_name)

    def test_get_sandbox_user(self) -> None:
        config = SandboxConfig()
        user = config.get_sandbox_user(user_id=456, timestamp=1704096000)

        assert user == "sandbox_user_456_1704096000"

    def test_get_template_schema_name(self) -> None:
        config = SandboxConfig()
        template_name = config.get_template_schema_name(lesson_id=5)

        assert template_name == "lesson_5_template"
        assert config.is_template_schema(template_name)

    def test_is_sandbox_schema(self) -> None:
        config = SandboxConfig()

        assert config.is_sandbox_schema("sandbox_user_123_1704096000") is True
        assert config.is_sandbox_schema("lesson_5_template") is False
        assert config.is_sandbox_schema("appdb") is False
        assert config.is_sandbox_schema("mysql") is False

    def test_is_template_schema(self) -> None:
        config = SandboxConfig()

        assert config.is_template_schema("lesson_5_template") is True
        assert config.is_template_schema("lesson_10_template") is True
        assert config.is_template_schema("sandbox_user_123_1704096000") is False
        assert config.is_template_schema("appdb") is False

    def test_custom_prefixes(self) -> None:
        config = SandboxConfig(
            schema_prefix="custom_sandbox_",
            template_prefix="tpl_lesson_",
            template_suffix="_v1",
        )

        schema_name = config.get_schema_name(user_id=1, timestamp=123)
        assert schema_name == "custom_sandbox_1_123"
        assert config.is_sandbox_schema(schema_name) is True

        template_name = config.get_template_schema_name(lesson_id=5)
        assert template_name == "tpl_lesson_5_v1"
        assert config.is_template_schema(template_name) is True

    def test_max_sandboxes_per_user_range(self) -> None:
        with pytest.raises(ValidationError):
            SandboxConfig(max_sandboxes_per_user=0)

        with pytest.raises(ValidationError):
            SandboxConfig(max_sandboxes_per_user=20)

        config = SandboxConfig(max_sandboxes_per_user=5)
        assert config.max_sandboxes_per_user == 5

    def test_query_timeout_range(self) -> None:
        with pytest.raises(ValidationError):
            SandboxConfig(query_timeout_seconds=0)

        with pytest.raises(ValidationError):
            SandboxConfig(query_timeout_seconds=500)

        config = SandboxConfig(query_timeout_seconds=60)
        assert config.query_timeout_seconds == 60

    def test_max_result_rows_range(self) -> None:
        with pytest.raises(ValidationError):
            SandboxConfig(max_result_rows=0)

        config = SandboxConfig(max_result_rows=5000)
        assert config.max_result_rows == 5000

    def test_enable_metrics_default(self) -> None:
        config = SandboxConfig()
        assert config.enable_metrics is True

    def test_enable_query_logging_default(self) -> None:
        config = SandboxConfig()
        assert config.enable_query_logging is False

    def test_all_limits_configured(self) -> None:
        config = SandboxConfig(
            max_active_sandboxes=500,
            max_sandboxes_per_user=2,
            idle_timeout_minutes=20,
            max_lifetime_hours=2,
            query_timeout_seconds=15,
            max_result_rows=500,
            max_query_memory_mb=50,
            rate_limit_queries_per_minute=30,
            max_schema_size_mb=50,
            max_connections_per_sandbox=3,
            cleanup_interval_minutes=10,
            cleanup_batch_size=5,
        )

        assert config.max_active_sandboxes == 500
        assert config.max_sandboxes_per_user == 2
        assert config.idle_timeout_minutes == 20
        assert config.max_lifetime_hours == 2
        assert config.query_timeout_seconds == 15
        assert config.max_result_rows == 500
        assert config.max_query_memory_mb == 50
        assert config.rate_limit_queries_per_minute == 30
        assert config.max_schema_size_mb == 50
        assert config.max_connections_per_sandbox == 3
        assert config.cleanup_interval_minutes == 10
        assert config.cleanup_batch_size == 5
