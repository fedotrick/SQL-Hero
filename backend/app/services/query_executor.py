"""
MySQL Query Executor with timeout and result comparison support.
"""

import asyncio
import hashlib
import re
from typing import Any

import aiomysql

from app.core.sandbox_config import SandboxConfig
from app.schemas.sandbox import QueryExecuteResponse, QueryValidationResult
from app.services.sandbox import IQueryExecutor, QueryValidator, Sandbox


class MySQLQueryExecutor(IQueryExecutor):
    """
    Production MySQL query executor with:
    - Timeout enforcement
    - Error sanitization
    - Result comparison (order-insensitive)
    """

    def __init__(self, config: SandboxConfig):
        self.config = config
        self.validator = QueryValidator(config)

    async def execute_query(
        self, sandbox: Sandbox, query: str, timeout: float | None = None
    ) -> QueryExecuteResponse:
        """Execute query with timeout enforcement."""
        validation = await self.validate_query(query)

        if not validation.is_valid:
            raise ValueError(f"Invalid query: {', '.join(validation.errors)}")

        query_timeout = timeout or self.config.query_timeout_seconds

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self._execute_with_connection(sandbox, query, validation.query_type),
                timeout=query_timeout,
            )
            return result
        except asyncio.TimeoutError as e:
            raise TimeoutError(
                f"Query execution exceeded timeout of {query_timeout} seconds"
            ) from e
        except Exception as e:
            # Sanitize error messages
            sanitized_error = self._sanitize_error(str(e))
            raise RuntimeError(f"Query execution failed: {sanitized_error}") from e

    async def _execute_with_connection(
        self, sandbox: Sandbox, query: str, query_type: str | None
    ) -> QueryExecuteResponse:
        """Execute query using aiomysql connection."""
        import time

        start_time = time.time()

        # Create connection to sandbox schema
        conn = await aiomysql.connect(
            host=self.config.mysql_host,
            port=self.config.mysql_port,
            user=self.config.mysql_admin_user,
            password=self.config.mysql_admin_password,
            db=sandbox.schema_name,
            autocommit=True,
        )

        try:
            async with conn.cursor() as cursor:
                # Set statement timeout
                await cursor.execute(
                    f"SET SESSION max_execution_time={self.config.query_timeout_seconds * 1000}"
                )

                # Execute the query
                await cursor.execute(query)

                # Fetch results
                if query_type == "SELECT" or query_type == "WITH":
                    rows = await cursor.fetchmany(self.config.max_result_rows)
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    row_count = len(rows)
                    affected_rows = None

                    # Convert rows to list of lists for JSON serialization
                    serializable_rows = [list(row) for row in rows]
                else:
                    # For DML statements
                    columns = []
                    serializable_rows = []
                    row_count = 0
                    affected_rows = cursor.rowcount

                execution_time = time.time() - start_time

                return QueryExecuteResponse(
                    columns=columns,
                    rows=serializable_rows,
                    row_count=row_count,
                    execution_time=execution_time,
                    affected_rows=affected_rows,
                )
        finally:
            conn.close()

    async def validate_query(self, query: str) -> QueryValidationResult:
        """Validate query using the validator."""
        return self.validator.validate(query)

    def _sanitize_error(self, error_message: str) -> str:
        """
        Sanitize error messages to avoid leaking sensitive information.
        Remove internal paths, IPs, and other sensitive data.
        """
        # Remove file paths
        error_message = re.sub(r"/[/\w.-]+", "[path]", error_message)

        # Remove IP addresses
        error_message = re.sub(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "[ip]", error_message)

        # Remove port numbers
        error_message = re.sub(r":(\d{4,5})", ":[port]", error_message)

        # Remove schema names that might leak information
        error_message = re.sub(r"sandbox_user_\d+_\d+", "[schema]", error_message)

        # Limit length
        if len(error_message) > 500:
            error_message = error_message[:500] + "..."

        return error_message

    def compare_results(
        self,
        user_result: QueryExecuteResponse,
        expected_result: dict[str, Any],
        ordered: bool = False,
    ) -> tuple[bool, list[str]]:
        """
        Compare user query result with expected result.

        Args:
            user_result: The result from user's query
            expected_result: Expected result dict with 'columns' and 'rows' keys
            ordered: Whether to compare in order (True) or order-insensitive (False)

        Returns:
            Tuple of (matches: bool, differences: list[str])
        """
        differences = []

        # Extract expected data
        expected_columns = expected_result.get("columns", [])
        expected_rows = expected_result.get("rows", [])

        # Compare columns
        if sorted(user_result.columns) != sorted(expected_columns):
            differences.append(
                f"Column mismatch. Expected: {expected_columns}, Got: {user_result.columns}"
            )

        # Compare row count
        if user_result.row_count != len(expected_rows):
            differences.append(
                f"Row count mismatch. Expected: {len(expected_rows)}, Got: {user_result.row_count}"
            )
            return False, differences

        # Compare rows
        if ordered:
            # Order-sensitive comparison
            if user_result.rows != expected_rows:
                differences.append("Row data mismatch (ordered comparison)")
                # Show first few differences
                for i, (user_row, expected_row) in enumerate(zip(user_result.rows, expected_rows)):
                    if user_row != expected_row:
                        differences.append(f"  Row {i}: Expected {expected_row}, Got {user_row}")
                        if len(differences) > 5:  # Limit to first 5 differences
                            differences.append("  ... (more differences)")
                            break
        else:
            # Order-insensitive comparison
            user_rows_normalized = self._normalize_rows(user_result.rows)
            expected_rows_normalized = self._normalize_rows(expected_rows)

            if user_rows_normalized != expected_rows_normalized:
                differences.append("Row data mismatch (order-insensitive comparison)")

                # Find missing and extra rows
                user_set = set(user_rows_normalized)
                expected_set = set(expected_rows_normalized)

                missing_rows = expected_set - user_set
                extra_rows = user_set - expected_set

                if missing_rows:
                    differences.append(f"  Missing rows: {list(missing_rows)[:3]}")
                if extra_rows:
                    differences.append(f"  Extra rows: {list(extra_rows)[:3]}")

        matches = len(differences) == 0
        return matches, differences

    def _normalize_rows(self, rows: list[list[Any]]) -> list[tuple]:
        """
        Normalize rows for order-insensitive comparison.
        Converts rows to hashable tuples and sorts them.
        """
        normalized = []
        for row in rows:
            # Convert row to tuple (hashable)
            normalized_row = tuple(self._normalize_value(val) for val in row)
            normalized.append(normalized_row)

        # Sort for consistent comparison
        return sorted(normalized)

    def _normalize_value(self, value: Any) -> Any:
        """Normalize a single value for comparison."""
        # Handle None
        if value is None:
            return None

        # Handle floats (round to avoid floating point precision issues)
        if isinstance(value, float):
            return round(value, 6)

        # Handle datetime (convert to ISO string)
        if hasattr(value, "isoformat"):
            return value.isoformat()

        # Handle bytes
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="ignore")

        return value
