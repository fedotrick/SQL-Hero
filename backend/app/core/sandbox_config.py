from typing import Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SandboxConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="SANDBOX_",
    )

    enabled: bool = Field(
        default=False,
        description="Enable sandbox functionality",
    )

    mysql_host: str = Field(
        default="localhost",
        description="MySQL host for sandbox schemas",
    )

    mysql_port: int = Field(
        default=3306,
        ge=1,
        le=65535,
        description="MySQL port",
    )

    mysql_admin_user: str = Field(
        default="sandbox_admin",
        description="MySQL administrative user for sandbox operations",
    )

    mysql_admin_password: str = Field(
        default="",
        description="MySQL administrative password",
    )

    mysql_database: str = Field(
        default="appdb",
        description="Main application database name",
    )

    max_active_sandboxes: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Maximum number of concurrent active sandboxes",
    )

    max_sandboxes_per_user: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum sandboxes per user",
    )

    idle_timeout_minutes: int = Field(
        default=30,
        ge=1,
        le=1440,
        description="Idle timeout in minutes before sandbox expires",
    )

    max_lifetime_hours: int = Field(
        default=4,
        ge=1,
        le=24,
        description="Maximum lifetime of a sandbox in hours",
    )

    query_timeout_seconds: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Maximum query execution time in seconds",
    )

    max_result_rows: int = Field(
        default=1000,
        ge=1,
        le=100000,
        description="Maximum number of rows to return from query",
    )

    max_query_memory_mb: int = Field(
        default=100,
        ge=1,
        le=1024,
        description="Maximum memory per query in megabytes",
    )

    rate_limit_queries_per_minute: int = Field(
        default=60,
        ge=1,
        le=1000,
        description="Maximum queries per minute per user",
    )

    max_schema_size_mb: int = Field(
        default=100,
        ge=1,
        le=1024,
        description="Maximum schema size in megabytes",
    )

    max_connections_per_sandbox: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum concurrent connections per sandbox",
    )

    cleanup_interval_minutes: int = Field(
        default=5,
        ge=1,
        le=60,
        description="Interval between cleanup runs in minutes",
    )

    cleanup_batch_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of sandboxes to cleanup per batch",
    )

    allowed_query_types: list[str] = Field(
        default=["SELECT", "INSERT", "UPDATE", "DELETE"],
        description="Allowed SQL query types",
    )

    blocked_patterns: list[str] = Field(
        default=[
            r"\bDROP\b",
            r"\bCREATE\s+(?:DATABASE|SCHEMA)\b",
            r"\bALTER\b",
            r"\bTRUNCATE\b",
            r"\bGRANT\b",
            r"\bREVOKE\b",
            r"\bSHUTDOWN\b",
            r"\bKILL\b",
            r"information_schema",
            r"mysql\.",
            r"performance_schema",
            r"sys\.",
        ],
        description="Regex patterns for blocked SQL commands",
    )

    enable_metrics: bool = Field(
        default=True,
        description="Enable metrics collection",
    )

    enable_query_logging: bool = Field(
        default=False,
        description="Enable query logging (privacy consideration)",
    )

    schema_prefix: str = Field(
        default="sandbox_user_",
        description="Prefix for sandbox schema names",
    )

    template_prefix: str = Field(
        default="lesson_",
        description="Prefix for lesson template schema names",
    )

    template_suffix: str = Field(
        default="_template",
        description="Suffix for lesson template schema names",
    )

    @field_validator("mysql_admin_password")
    @classmethod
    def validate_admin_password(cls, v: str, info: Any) -> str:
        if info.data.get("enabled") and not v:
            raise ValueError("mysql_admin_password is required when sandbox is enabled")
        return v

    @field_validator("allowed_query_types")
    @classmethod
    def validate_allowed_query_types(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("allowed_query_types cannot be empty")

        valid_types = {"SELECT", "INSERT", "UPDATE", "DELETE", "WITH"}
        for query_type in v:
            if query_type.upper() not in valid_types:
                raise ValueError(f"Invalid query type: {query_type}")

        return [qt.upper() for qt in v]

    @field_validator("blocked_patterns")
    @classmethod
    def validate_blocked_patterns(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("blocked_patterns cannot be empty")
        return v

    @model_validator(mode="after")
    def validate_timeouts(self) -> "SandboxConfig":
        idle_minutes = self.idle_timeout_minutes
        max_hours = self.max_lifetime_hours

        if idle_minutes > max_hours * 60:
            raise ValueError(
                f"idle_timeout_minutes ({idle_minutes}) cannot be greater than "
                f"max_lifetime_hours ({max_hours} hours = {max_hours * 60} minutes)"
            )

        return self

    @model_validator(mode="after")
    def validate_cleanup_interval(self) -> "SandboxConfig":
        if self.cleanup_interval_minutes > self.idle_timeout_minutes:
            raise ValueError(
                f"cleanup_interval_minutes ({self.cleanup_interval_minutes}) should not be "
                f"greater than idle_timeout_minutes ({self.idle_timeout_minutes})"
            )

        return self

    def get_schema_name(self, user_id: int, timestamp: int) -> str:
        return f"{self.schema_prefix}{user_id}_{timestamp}"

    def get_sandbox_user(self, user_id: int, timestamp: int) -> str:
        return f"{self.schema_prefix}{user_id}_{timestamp}"

    def get_template_schema_name(self, lesson_id: int) -> str:
        return f"{self.template_prefix}{lesson_id}{self.template_suffix}"

    def is_sandbox_schema(self, schema_name: str) -> bool:
        return schema_name.startswith(self.schema_prefix)

    def is_template_schema(self, schema_name: str) -> bool:
        return schema_name.startswith(self.template_prefix) and schema_name.endswith(
            self.template_suffix
        )


def get_sandbox_config() -> SandboxConfig:
    return SandboxConfig()
