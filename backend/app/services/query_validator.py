"""
Query validation guard for SQL sandbox environments.

Provides comprehensive validation including:
- SQL injection prevention
- Destructive command blocking
- System table protection
- Lesson-specific query type restrictions
- Clear validation messages
"""

import re
from dataclasses import dataclass
from typing import ClassVar

from app.core.sandbox_config import SandboxConfig
from app.schemas.sandbox import QueryValidationResult


@dataclass
class LessonQueryPolicy:
    """Query policy configuration for specific lessons or modules."""

    lesson_id: int | None = None
    module_id: int | None = None
    allowed_query_types: list[str] | None = None
    custom_blocked_patterns: list[str] | None = None
    custom_messages: dict[str, str] | None = None

    def get_allowed_types(self, default: list[str]) -> list[str]:
        """Get allowed query types, falling back to default if not specified."""
        return self.allowed_query_types if self.allowed_query_types is not None else default

    def get_blocked_patterns(self, default: list[str]) -> list[str]:
        """Get blocked patterns, adding custom patterns to defaults."""
        patterns = list(default)
        if self.custom_blocked_patterns:
            patterns.extend(self.custom_blocked_patterns)
        return patterns


class QueryValidator:
    """
    Validates SQL queries against security policies and lesson-specific rules.

    Features:
    - Blocks destructive commands (DROP, TRUNCATE, ALTER)
    - Prevents access to system schemas
    - Enforces lesson-specific query type restrictions
    - Detects common SQL injection patterns
    - Provides clear, actionable error messages
    """

    # SQL keywords that indicate query type
    QUERY_TYPE_PATTERNS: ClassVar[list[tuple[str, str]]] = [
        ("SELECT", r"^\s*(?:WITH\s+.+\s+AS\s+.+\s+)?SELECT\b"),
        ("INSERT", r"^\s*INSERT\b"),
        ("UPDATE", r"^\s*UPDATE\b"),
        ("DELETE", r"^\s*DELETE\b"),
        ("WITH", r"^\s*WITH\b"),
        ("CREATE", r"^\s*CREATE\b"),
        ("DROP", r"^\s*DROP\b"),
        ("ALTER", r"^\s*ALTER\b"),
        ("TRUNCATE", r"^\s*TRUNCATE\b"),
    ]

    # Additional dangerous patterns to block
    DANGEROUS_PATTERNS: ClassVar[list[tuple[str, str]]] = [
        ("UNION-based injection", r"\bUNION\s+(?:ALL\s+)?SELECT\b"),
        ("Stacked queries", r";\s*(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b"),
        ("Comment-based bypass", r"--\s*$|/\*.*?\*/|#"),
        ("System variables", r"@@\w+"),
        ("OUTFILE operation", r"\bINTO\s+(?:OUT|DUMP)FILE\b"),
        ("LOAD DATA operation", r"\bLOAD\s+DATA\b"),
        ("System function calls", r"\b(?:LOAD_FILE|SYSTEM|EXEC)\s*\("),
    ]

    # System schemas that should never be accessed
    SYSTEM_SCHEMAS: ClassVar[list[str]] = [
        "information_schema",
        "mysql",
        "performance_schema",
        "sys",
    ]

    def __init__(self, config: SandboxConfig, lesson_policy: LessonQueryPolicy | None = None):
        """
        Initialize validator with configuration and optional lesson-specific policy.

        Args:
            config: Global sandbox configuration
            lesson_policy: Optional lesson-specific policy overrides
        """
        self.config = config
        self.lesson_policy = lesson_policy or LessonQueryPolicy()

        # Compile regex patterns for performance
        blocked_patterns = self.lesson_policy.get_blocked_patterns(config.blocked_patterns)
        self._compiled_blocked_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in blocked_patterns
        ]

        self._compiled_dangerous_patterns = [
            (name, re.compile(pattern, re.IGNORECASE)) for name, pattern in self.DANGEROUS_PATTERNS
        ]

        # Get effective allowed query types
        self.allowed_query_types = self.lesson_policy.get_allowed_types(config.allowed_query_types)

    def validate(self, query: str, lesson_id: int | None = None) -> QueryValidationResult:
        """
        Validate a SQL query against all security and policy rules.

        Args:
            query: SQL query string to validate
            lesson_id: Optional lesson ID for context-specific validation

        Returns:
            QueryValidationResult with validation status, errors, and warnings
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Basic validation
        query_stripped = query.strip()
        if not query_stripped:
            return QueryValidationResult(
                is_valid=False,
                errors=["Query cannot be empty"],
                warnings=[],
                query_type=None,
            )

        # Detect query type
        query_upper = query_stripped.upper()
        detected_type = self._detect_query_type(query_upper)

        # Check for blocked patterns (destructive commands)
        for pattern in self._compiled_blocked_patterns:
            match = pattern.search(query)
            if match:
                errors.append(
                    f"Query contains blocked operation: '{match.group(0)}'. "
                    f"This operation is not allowed in sandbox environments."
                )

        # Check for dangerous patterns (SQL injection attempts)
        for pattern_name, pattern in self._compiled_dangerous_patterns:
            if pattern.search(query):
                errors.append(
                    f"Query contains potentially dangerous pattern ({pattern_name}). "
                    f"This is blocked for security reasons."
                )

        # Check for system schema access
        for schema in self.SYSTEM_SCHEMAS:
            if re.search(rf"\b{schema}\.", query, re.IGNORECASE):
                errors.append(
                    f"Access to system schema '{schema}' is not allowed. "
                    f"Please query only the lesson tables in your sandbox."
                )

        # Check query type against allowed types
        if detected_type and detected_type not in self.allowed_query_types:
            allowed_str = ", ".join(self.allowed_query_types)
            if lesson_id:
                errors.append(
                    f"Query type '{detected_type}' is not allowed for this lesson. "
                    f"This lesson only allows: {allowed_str}"
                )
            else:
                errors.append(
                    f"Query type '{detected_type}' is not allowed. Allowed types: {allowed_str}"
                )

        # Quality warnings
        if query_upper.count("SELECT") > 10:
            warnings.append(
                "Query contains many SELECT statements. Consider simplifying your query."
            )

        if len(query) > 5000:
            warnings.append(
                "Query is very long (>5000 characters). Consider breaking it into smaller parts."
            )

        # Check for potentially unintended patterns
        if re.search(r"\bDELETE\s+FROM\s+\w+\s*(?:;|$)", query, re.IGNORECASE):
            warnings.append(
                "DELETE without WHERE clause detected. This will remove all rows. "
                "Is this intentional?"
            )

        if re.search(r"\bUPDATE\s+\w+\s+SET\s+.+?(?:;|$)(?!.*WHERE)", query, re.IGNORECASE):
            warnings.append(
                "UPDATE without WHERE clause detected. This will affect all rows. "
                "Is this intentional?"
            )

        is_valid = len(errors) == 0

        return QueryValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            query_type=detected_type,
        )

    def _detect_query_type(self, query_upper: str) -> str | None:
        """
        Detect the primary type of SQL query.

        Args:
            query_upper: Query string in uppercase

        Returns:
            Query type string or None if not detected
        """
        for query_type, pattern in self.QUERY_TYPE_PATTERNS:
            if re.match(pattern, query_upper):
                return query_type
        return None

    def get_policy_description(self) -> str:
        """Get a human-readable description of the current validation policy."""
        allowed = ", ".join(self.allowed_query_types)
        if self.lesson_policy.lesson_id:
            return f"Lesson {self.lesson_policy.lesson_id} allows: {allowed}"
        elif self.lesson_policy.module_id:
            return f"Module {self.lesson_policy.module_id} allows: {allowed}"
        else:
            return f"Default policy allows: {allowed}"


def create_lesson_validator(
    config: SandboxConfig, lesson_id: int, allowed_types: list[str] | None = None
) -> QueryValidator:
    """
    Factory function to create a validator for a specific lesson.

    Args:
        config: Global sandbox configuration
        lesson_id: Lesson ID for context
        allowed_types: Override allowed query types for this lesson

    Returns:
        Configured QueryValidator instance
    """
    policy = LessonQueryPolicy(lesson_id=lesson_id, allowed_query_types=allowed_types)
    return QueryValidator(config, policy)


def create_module_validator(
    config: SandboxConfig, module_id: int, allowed_types: list[str] | None = None
) -> QueryValidator:
    """
    Factory function to create a validator for a specific module.

    Args:
        config: Global sandbox configuration
        module_id: Module ID for context
        allowed_types: Override allowed query types for this module

    Returns:
        Configured QueryValidator instance
    """
    policy = LessonQueryPolicy(module_id=module_id, allowed_query_types=allowed_types)
    return QueryValidator(config, policy)
