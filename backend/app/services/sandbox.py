import re
import time
from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.sandbox_config import SandboxConfig
from app.schemas.sandbox import (
    CleanupResult,
    QueryExecuteResponse,
    QueryValidationResult,
    SandboxStatus,
)


class Sandbox:
    def __init__(
        self,
        sandbox_id: str,
        user_id: int,
        lesson_id: int,
        schema_name: str,
        status: SandboxStatus,
        created_at: datetime,
        expires_at: datetime,
        last_accessed_at: datetime,
        query_count: int = 0,
    ):
        self.sandbox_id = sandbox_id
        self.user_id = user_id
        self.lesson_id = lesson_id
        self.schema_name = schema_name
        self.status = status
        self.created_at = created_at
        self.expires_at = expires_at
        self.last_accessed_at = last_accessed_at
        self.query_count = query_count

    def is_expired(self, now: datetime | None = None) -> bool:
        if now is None:
            now = datetime.now(UTC)
        return now >= self.expires_at

    def update_access(self) -> None:
        self.last_accessed_at = datetime.now(UTC)
        self.query_count += 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "sandbox_id": self.sandbox_id,
            "user_id": self.user_id,
            "lesson_id": self.lesson_id,
            "schema_name": self.schema_name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "last_accessed_at": self.last_accessed_at.isoformat(),
            "query_count": self.query_count,
        }


class ISandboxManager(ABC):
    @abstractmethod
    async def create_sandbox(self, user_id: int, lesson_id: int) -> Sandbox:
        pass

    @abstractmethod
    async def get_sandbox(self, sandbox_id: str) -> Sandbox | None:
        pass

    @abstractmethod
    async def get_user_sandboxes(self, user_id: int) -> list[Sandbox]:
        pass

    @abstractmethod
    async def destroy_sandbox(self, sandbox_id: str) -> None:
        pass

    @abstractmethod
    async def cleanup_expired_sandboxes(self) -> CleanupResult:
        pass

    @abstractmethod
    async def update_sandbox_access(self, sandbox_id: str) -> None:
        pass


class ISchemaManager(ABC):
    @abstractmethod
    async def create_schema(self, schema_name: str) -> None:
        pass

    @abstractmethod
    async def seed_data(self, schema_name: str, lesson_id: int) -> None:
        pass

    @abstractmethod
    async def drop_schema(self, schema_name: str) -> None:
        pass

    @abstractmethod
    async def schema_exists(self, schema_name: str) -> bool:
        pass

    @abstractmethod
    async def get_schema_size(self, schema_name: str) -> int:
        pass

    @abstractmethod
    async def create_sandbox_user(self, username: str, password: str, schema_name: str) -> None:
        pass

    @abstractmethod
    async def drop_sandbox_user(self, username: str) -> None:
        pass


class IQueryExecutor(ABC):
    @abstractmethod
    async def execute_query(self, sandbox: Sandbox, query: str) -> QueryExecuteResponse:
        pass

    @abstractmethod
    async def validate_query(self, query: str) -> QueryValidationResult:
        pass


class QueryValidator:
    def __init__(self, config: SandboxConfig):
        self.config = config
        self._compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in config.blocked_patterns
        ]

    def validate(self, query: str) -> QueryValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        query_stripped = query.strip()
        if not query_stripped:
            errors.append("Query cannot be empty")
            return QueryValidationResult(is_valid=False, errors=errors, warnings=warnings)

        for pattern in self._compiled_patterns:
            if pattern.search(query):
                errors.append(f"Query contains blocked pattern: {pattern.pattern}")

        query_upper = query_stripped.upper()
        detected_type = self._detect_query_type(query_upper)

        if detected_type and detected_type not in self.config.allowed_query_types:
            errors.append(f"Query type '{detected_type}' is not allowed")

        if query_upper.count("SELECT") > 10:
            warnings.append("Query contains many SELECT statements, consider simplifying")

        if len(query) > 5000:
            warnings.append("Query is very long, consider breaking it into smaller parts")

        is_valid = len(errors) == 0

        return QueryValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            query_type=detected_type,
        )

    def _detect_query_type(self, query_upper: str) -> str | None:
        query_type_patterns = [
            ("SELECT", r"^\s*(?:WITH\s+.+\s+AS\s+.+\s+)?SELECT\b"),
            ("INSERT", r"^\s*INSERT\b"),
            ("UPDATE", r"^\s*UPDATE\b"),
            ("DELETE", r"^\s*DELETE\b"),
            ("WITH", r"^\s*WITH\b"),
        ]

        for query_type, pattern in query_type_patterns:
            if re.match(pattern, query_upper):
                return query_type

        return None


class InMemorySandboxManager(ISandboxManager):
    def __init__(self, config: SandboxConfig):
        self.config = config
        self._sandboxes: dict[str, Sandbox] = {}
        self._user_sandbox_ids: dict[int, list[str]] = {}

    async def create_sandbox(self, user_id: int, lesson_id: int) -> Sandbox:
        user_sandboxes = await self.get_user_sandboxes(user_id)
        active_count = sum(1 for s in user_sandboxes if s.status == SandboxStatus.ACTIVE)

        if active_count >= self.config.max_sandboxes_per_user:
            raise ValueError(
                f"User has reached maximum of {self.config.max_sandboxes_per_user} active sandboxes"
            )

        if len(self._sandboxes) >= self.config.max_active_sandboxes:
            raise ValueError(
                f"System has reached maximum of {self.config.max_active_sandboxes} active sandboxes"
            )

        now = datetime.now(UTC)
        timestamp = int(time.time())
        sandbox_id = f"{user_id}_{lesson_id}_{timestamp}"
        schema_name = self.config.get_schema_name(user_id, timestamp)

        expires_at = now + timedelta(hours=self.config.max_lifetime_hours)

        sandbox = Sandbox(
            sandbox_id=sandbox_id,
            user_id=user_id,
            lesson_id=lesson_id,
            schema_name=schema_name,
            status=SandboxStatus.CREATING,
            created_at=now,
            expires_at=expires_at,
            last_accessed_at=now,
            query_count=0,
        )

        self._sandboxes[sandbox_id] = sandbox

        if user_id not in self._user_sandbox_ids:
            self._user_sandbox_ids[user_id] = []
        self._user_sandbox_ids[user_id].append(sandbox_id)

        return sandbox

    async def get_sandbox(self, sandbox_id: str) -> Sandbox | None:
        return self._sandboxes.get(sandbox_id)

    async def get_user_sandboxes(self, user_id: int) -> list[Sandbox]:
        sandbox_ids = self._user_sandbox_ids.get(user_id, [])
        return [self._sandboxes[sid] for sid in sandbox_ids if sid in self._sandboxes]

    async def destroy_sandbox(self, sandbox_id: str) -> None:
        sandbox = self._sandboxes.get(sandbox_id)
        if sandbox:
            sandbox.status = SandboxStatus.DESTROYED
            del self._sandboxes[sandbox_id]

            if sandbox.user_id in self._user_sandbox_ids:
                self._user_sandbox_ids[sandbox.user_id] = [
                    sid for sid in self._user_sandbox_ids[sandbox.user_id] if sid != sandbox_id
                ]

    async def cleanup_expired_sandboxes(self) -> CleanupResult:
        start_time = time.time()
        now = datetime.now(UTC)

        expired_ids = [
            sid
            for sid, sandbox in self._sandboxes.items()
            if sandbox.is_expired(now) and sandbox.status == SandboxStatus.ACTIVE
        ]

        cleaned_ids = []
        failed_count = 0

        batch_ids = expired_ids[: self.config.cleanup_batch_size]

        for sandbox_id in batch_ids:
            try:
                await self.destroy_sandbox(sandbox_id)
                cleaned_ids.append(sandbox_id)
            except Exception:
                failed_count += 1

        duration = time.time() - start_time

        return CleanupResult(
            cleaned_count=len(cleaned_ids),
            failed_count=failed_count,
            duration=duration,
            cleaned_sandbox_ids=cleaned_ids,
        )

    async def update_sandbox_access(self, sandbox_id: str) -> None:
        sandbox = await self.get_sandbox(sandbox_id)
        if sandbox:
            sandbox.update_access()

            idle_timeout = timedelta(minutes=self.config.idle_timeout_minutes)
            new_expires = datetime.now(UTC) + idle_timeout

            if new_expires < sandbox.expires_at:
                sandbox.expires_at = new_expires


class MockSchemaManager(ISchemaManager):
    def __init__(self, config: SandboxConfig):
        self.config = config
        self._schemas: set[str] = set()
        self._users: set[str] = set()

    async def create_schema(self, schema_name: str) -> None:
        if schema_name in self._schemas:
            raise ValueError(f"Schema {schema_name} already exists")
        self._schemas.add(schema_name)

    async def seed_data(self, schema_name: str, lesson_id: int) -> None:
        if schema_name not in self._schemas:
            raise ValueError(f"Schema {schema_name} does not exist")

    async def drop_schema(self, schema_name: str) -> None:
        self._schemas.discard(schema_name)

    async def schema_exists(self, schema_name: str) -> bool:
        return schema_name in self._schemas

    async def get_schema_size(self, schema_name: str) -> int:
        return 0 if schema_name in self._schemas else -1

    async def create_sandbox_user(self, username: str, password: str, schema_name: str) -> None:
        self._users.add(username)

    async def drop_sandbox_user(self, username: str) -> None:
        self._users.discard(username)


class MockQueryExecutor(IQueryExecutor):
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.validator = QueryValidator(config)

    async def execute_query(self, sandbox: Sandbox, query: str) -> QueryExecuteResponse:
        validation = await self.validate_query(query)

        if not validation.is_valid:
            raise ValueError(f"Invalid query: {', '.join(validation.errors)}")

        start_time = time.time()

        columns = ["id", "name", "value"]
        rows = [
            [1, "Sample A", 100],
            [2, "Sample B", 200],
        ]

        execution_time = time.time() - start_time

        return QueryExecuteResponse(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            execution_time=execution_time,
            affected_rows=None if validation.query_type == "SELECT" else 0,
        )

    async def validate_query(self, query: str) -> QueryValidationResult:
        return self.validator.validate(query)


class SandboxService:
    def __init__(
        self,
        config: SandboxConfig,
        sandbox_manager: ISandboxManager,
        schema_manager: ISchemaManager,
        query_executor: IQueryExecutor,
    ):
        self.config = config
        self.sandbox_manager = sandbox_manager
        self.schema_manager = schema_manager
        self.query_executor = query_executor

    async def create_sandbox(self, user_id: int, lesson_id: int) -> Sandbox:
        if not self.config.enabled:
            raise RuntimeError("Sandbox functionality is not enabled")

        sandbox = await self.sandbox_manager.create_sandbox(user_id, lesson_id)

        try:
            await self.schema_manager.create_schema(sandbox.schema_name)

            password = self._generate_password()
            await self.schema_manager.create_sandbox_user(
                username=self.config.get_sandbox_user(user_id, int(time.time())),
                password=password,
                schema_name=sandbox.schema_name,
            )

            await self.schema_manager.seed_data(sandbox.schema_name, lesson_id)

            sandbox.status = SandboxStatus.ACTIVE

        except Exception as e:
            sandbox.status = SandboxStatus.ERROR
            await self.sandbox_manager.destroy_sandbox(sandbox.sandbox_id)
            raise RuntimeError(f"Failed to create sandbox: {e}") from e

        return sandbox

    async def execute_query(self, sandbox_id: str, query: str) -> QueryExecuteResponse:
        if not self.config.enabled:
            raise RuntimeError("Sandbox functionality is not enabled")

        sandbox = await self.sandbox_manager.get_sandbox(sandbox_id)
        if not sandbox:
            raise ValueError(f"Sandbox {sandbox_id} not found")

        if sandbox.status != SandboxStatus.ACTIVE:
            raise ValueError(f"Sandbox {sandbox_id} is not active (status: {sandbox.status})")

        if sandbox.is_expired():
            sandbox.status = SandboxStatus.EXPIRED
            raise ValueError(f"Sandbox {sandbox_id} has expired")

        result = await self.query_executor.execute_query(sandbox, query)

        await self.sandbox_manager.update_sandbox_access(sandbox_id)

        return result

    async def destroy_sandbox(self, sandbox_id: str) -> None:
        if not self.config.enabled:
            raise RuntimeError("Sandbox functionality is not enabled")

        sandbox = await self.sandbox_manager.get_sandbox(sandbox_id)
        if not sandbox:
            raise ValueError(f"Sandbox {sandbox_id} not found")

        try:
            await self.schema_manager.drop_schema(sandbox.schema_name)

            username = self.config.get_sandbox_user(sandbox.user_id, int(time.time()))
            await self.schema_manager.drop_sandbox_user(username)

        finally:
            await self.sandbox_manager.destroy_sandbox(sandbox_id)

    async def cleanup_expired(self) -> CleanupResult:
        if not self.config.enabled:
            raise RuntimeError("Sandbox functionality is not enabled")

        return await self.sandbox_manager.cleanup_expired_sandboxes()

    def _generate_password(self, length: int = 32) -> str:
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))
