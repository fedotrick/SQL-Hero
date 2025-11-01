from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SandboxStatus(str, Enum):
    CREATING = "creating"
    ACTIVE = "active"
    EXPIRED = "expired"
    DESTROYED = "destroyed"
    ERROR = "error"


class SandboxCreateRequest(BaseModel):
    lesson_id: int = Field(..., ge=1, description="Lesson ID for dataset seeding")


class SandboxCreateResponse(BaseModel):
    sandbox_id: str = Field(..., description="Unique sandbox identifier")
    schema_name: str = Field(..., description="Database schema name")
    status: SandboxStatus = Field(..., description="Current sandbox status")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")


class QueryExecuteRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000, description="SQL query to execute")
    validate_against_expected: bool = Field(
        default=False, description="Whether to validate against expected result"
    )


class QueryExecuteResponse(BaseModel):
    columns: list[str] = Field(default=[], description="Column names")
    rows: list[list[Any]] = Field(default=[], description="Result rows")
    row_count: int = Field(..., ge=0, description="Number of rows returned")
    execution_time: float = Field(..., ge=0, description="Query execution time in seconds")
    affected_rows: int | None = Field(default=None, description="Rows affected (for DML)")


class QueryValidateResponse(BaseModel):
    """Response for query validation with expected result comparison."""

    passed: bool = Field(..., description="Whether the query result matches expected")
    result: QueryExecuteResponse = Field(..., description="Query execution result")
    differences: list[str] = Field(default=[], description="Differences from expected result")
    message: str = Field(..., description="Human-readable message about the result")


class QueryValidationResult(BaseModel):
    is_valid: bool = Field(..., description="Whether query is valid")
    errors: list[str] = Field(default=[], description="Validation error messages")
    warnings: list[str] = Field(default=[], description="Validation warnings")
    query_type: str | None = Field(default=None, description="Detected query type")


class SandboxStatusResponse(BaseModel):
    sandbox_id: str = Field(..., description="Unique sandbox identifier")
    schema_name: str = Field(..., description="Database schema name")
    status: SandboxStatus = Field(..., description="Current sandbox status")
    created_at: datetime = Field(..., description="Creation timestamp")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    last_accessed_at: datetime = Field(..., description="Last query execution timestamp")
    query_count: int = Field(..., ge=0, description="Total queries executed")
    lesson_id: int = Field(..., ge=1, description="Associated lesson ID")


class SandboxDestroyResponse(BaseModel):
    sandbox_id: str = Field(..., description="Destroyed sandbox identifier")
    status: SandboxStatus = Field(..., description="Final status")
    destroyed_at: datetime = Field(..., description="Destruction timestamp")


class SandboxMetrics(BaseModel):
    total_sandboxes_created: int = Field(..., ge=0)
    active_sandboxes: int = Field(..., ge=0)
    expired_sandboxes: int = Field(..., ge=0)
    total_queries_executed: int = Field(..., ge=0)
    average_query_time: float = Field(..., ge=0)
    average_sandbox_lifetime: float = Field(..., ge=0)


class CleanupResult(BaseModel):
    cleaned_count: int = Field(..., ge=0, description="Number of sandboxes cleaned up")
    failed_count: int = Field(..., ge=0, description="Number of cleanup failures")
    duration: float = Field(..., ge=0, description="Cleanup duration in seconds")
    cleaned_sandbox_ids: list[str] = Field(default=[], description="IDs of cleaned sandboxes")
