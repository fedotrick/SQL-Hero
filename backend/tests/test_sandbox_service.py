import pytest

from app.core.sandbox_config import SandboxConfig
from app.schemas.sandbox import QueryValidationResult, SandboxStatus
from app.services.sandbox import (
    InMemorySandboxManager,
    MockQueryExecutor,
    MockSchemaManager,
    QueryValidator,
    SandboxService,
)


@pytest.fixture
def sandbox_config() -> SandboxConfig:
    return SandboxConfig(
        enabled=True,
        mysql_admin_password="test_password",
        max_sandboxes_per_user=3,
        max_active_sandboxes=10,
        idle_timeout_minutes=30,
        max_lifetime_hours=4,
    )


@pytest.fixture
def sandbox_manager(sandbox_config: SandboxConfig) -> InMemorySandboxManager:
    return InMemorySandboxManager(sandbox_config)


@pytest.fixture
def schema_manager(sandbox_config: SandboxConfig) -> MockSchemaManager:
    return MockSchemaManager(sandbox_config)


@pytest.fixture
def query_executor(sandbox_config: SandboxConfig) -> MockQueryExecutor:
    return MockQueryExecutor(sandbox_config)


@pytest.fixture
def sandbox_service(
    sandbox_config: SandboxConfig,
    sandbox_manager: InMemorySandboxManager,
    schema_manager: MockSchemaManager,
    query_executor: MockQueryExecutor,
) -> SandboxService:
    return SandboxService(
        config=sandbox_config,
        sandbox_manager=sandbox_manager,
        schema_manager=schema_manager,
        query_executor=query_executor,
    )


class TestQueryValidator:
    def test_validate_empty_query(self, sandbox_config: SandboxConfig) -> None:
        validator = QueryValidator(sandbox_config)
        result = validator.validate("")

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "empty" in result.errors[0].lower()

    def test_validate_select_query(self, sandbox_config: SandboxConfig) -> None:
        validator = QueryValidator(sandbox_config)
        result = validator.validate("SELECT * FROM employees")

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.query_type == "SELECT"

    def test_validate_insert_query(self, sandbox_config: SandboxConfig) -> None:
        validator = QueryValidator(sandbox_config)
        result = validator.validate("INSERT INTO users (name) VALUES ('John')")

        assert result.is_valid is True
        assert result.query_type == "INSERT"

    def test_validate_update_query(self, sandbox_config: SandboxConfig) -> None:
        validator = QueryValidator(sandbox_config)
        result = validator.validate("UPDATE users SET name = 'Jane' WHERE id = 1")

        assert result.is_valid is True
        assert result.query_type == "UPDATE"

    def test_validate_delete_query(self, sandbox_config: SandboxConfig) -> None:
        validator = QueryValidator(sandbox_config)
        result = validator.validate("DELETE FROM users WHERE id = 1")

        assert result.is_valid is True
        assert result.query_type == "DELETE"

    def test_validate_drop_blocked(self, sandbox_config: SandboxConfig) -> None:
        validator = QueryValidator(sandbox_config)
        result = validator.validate("DROP TABLE users")

        assert result.is_valid is False
        assert any("blocked pattern" in error.lower() for error in result.errors)

    def test_validate_create_database_blocked(self, sandbox_config: SandboxConfig) -> None:
        validator = QueryValidator(sandbox_config)
        result = validator.validate("CREATE DATABASE newdb")

        assert result.is_valid is False
        assert any("blocked pattern" in error.lower() for error in result.errors)

    def test_validate_alter_blocked(self, sandbox_config: SandboxConfig) -> None:
        validator = QueryValidator(sandbox_config)
        result = validator.validate("ALTER TABLE users ADD COLUMN age INT")

        assert result.is_valid is False
        assert any("blocked pattern" in error.lower() for error in result.errors)

    def test_validate_truncate_blocked(self, sandbox_config: SandboxConfig) -> None:
        validator = QueryValidator(sandbox_config)
        result = validator.validate("TRUNCATE TABLE users")

        assert result.is_valid is False
        assert any("blocked pattern" in error.lower() for error in result.errors)

    def test_validate_information_schema_blocked(self, sandbox_config: SandboxConfig) -> None:
        validator = QueryValidator(sandbox_config)
        result = validator.validate("SELECT * FROM information_schema.tables")

        assert result.is_valid is False
        assert any("blocked pattern" in error.lower() for error in result.errors)

    def test_validate_mysql_schema_blocked(self, sandbox_config: SandboxConfig) -> None:
        validator = QueryValidator(sandbox_config)
        result = validator.validate("SELECT * FROM mysql.user")

        assert result.is_valid is False
        assert any("blocked pattern" in error.lower() for error in result.errors)

    def test_validate_with_cte(self, sandbox_config: SandboxConfig) -> None:
        validator = QueryValidator(sandbox_config)
        query = """
        WITH high_earners AS (
            SELECT * FROM employees WHERE salary > 100000
        )
        SELECT * FROM high_earners
        """
        result = validator.validate(query)

        assert result.is_valid is True
        assert result.query_type == "SELECT"

    def test_validate_long_query_warning(self, sandbox_config: SandboxConfig) -> None:
        validator = QueryValidator(sandbox_config)
        result = validator.validate("SELECT * FROM users" + " " * 5000)

        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert any("long" in warning.lower() for warning in result.warnings)

    def test_validate_disallowed_query_type(self, sandbox_config: SandboxConfig) -> None:
        config = SandboxConfig(
            allowed_query_types=["SELECT"],
            blocked_patterns=[r"\bDROP\b"],
        )
        validator = QueryValidator(config)
        result = validator.validate("INSERT INTO users (name) VALUES ('John')")

        assert result.is_valid is False
        assert any("not allowed" in error.lower() for error in result.errors)


class TestInMemorySandboxManager:
    async def test_create_sandbox(self, sandbox_manager: InMemorySandboxManager) -> None:
        sandbox = await sandbox_manager.create_sandbox(user_id=1, lesson_id=5)

        assert sandbox.sandbox_id is not None
        assert sandbox.user_id == 1
        assert sandbox.lesson_id == 5
        assert sandbox.status == SandboxStatus.CREATING
        assert sandbox.query_count == 0

    async def test_get_sandbox(self, sandbox_manager: InMemorySandboxManager) -> None:
        created = await sandbox_manager.create_sandbox(user_id=1, lesson_id=5)

        retrieved = await sandbox_manager.get_sandbox(created.sandbox_id)

        assert retrieved is not None
        assert retrieved.sandbox_id == created.sandbox_id
        assert retrieved.user_id == created.user_id

    async def test_get_nonexistent_sandbox(self, sandbox_manager: InMemorySandboxManager) -> None:
        retrieved = await sandbox_manager.get_sandbox("nonexistent_id")
        assert retrieved is None

    async def test_get_user_sandboxes(self, sandbox_manager: InMemorySandboxManager) -> None:
        await sandbox_manager.create_sandbox(user_id=1, lesson_id=5)
        await sandbox_manager.create_sandbox(user_id=1, lesson_id=6)
        await sandbox_manager.create_sandbox(user_id=2, lesson_id=5)

        user1_sandboxes = await sandbox_manager.get_user_sandboxes(user_id=1)
        user2_sandboxes = await sandbox_manager.get_user_sandboxes(user_id=2)

        assert len(user1_sandboxes) == 2
        assert len(user2_sandboxes) == 1

    async def test_destroy_sandbox(self, sandbox_manager: InMemorySandboxManager) -> None:
        created = await sandbox_manager.create_sandbox(user_id=1, lesson_id=5)

        await sandbox_manager.destroy_sandbox(created.sandbox_id)

        retrieved = await sandbox_manager.get_sandbox(created.sandbox_id)
        assert retrieved is None

    async def test_max_sandboxes_per_user(
        self, sandbox_config: SandboxConfig, sandbox_manager: InMemorySandboxManager
    ) -> None:
        for i in range(sandbox_config.max_sandboxes_per_user):
            sandbox = await sandbox_manager.create_sandbox(user_id=1, lesson_id=i + 1)
            sandbox.status = SandboxStatus.ACTIVE

        with pytest.raises(ValueError) as exc_info:
            await sandbox_manager.create_sandbox(user_id=1, lesson_id=99)

        assert "maximum" in str(exc_info.value).lower()
        assert str(sandbox_config.max_sandboxes_per_user) in str(exc_info.value)

    async def test_update_sandbox_access(self, sandbox_manager: InMemorySandboxManager) -> None:
        created = await sandbox_manager.create_sandbox(user_id=1, lesson_id=5)
        created.status = SandboxStatus.ACTIVE

        initial_access_time = created.last_accessed_at
        initial_query_count = created.query_count

        await sandbox_manager.update_sandbox_access(created.sandbox_id)

        assert created.last_accessed_at > initial_access_time
        assert created.query_count == initial_query_count + 1

    async def test_cleanup_expired_sandboxes(self, sandbox_manager: InMemorySandboxManager) -> None:
        from datetime import UTC, datetime, timedelta

        sandbox1 = await sandbox_manager.create_sandbox(user_id=1, lesson_id=5)
        sandbox1.status = SandboxStatus.ACTIVE
        sandbox1.expires_at = datetime.now(UTC) - timedelta(hours=1)

        sandbox2 = await sandbox_manager.create_sandbox(user_id=2, lesson_id=6)
        sandbox2.status = SandboxStatus.ACTIVE
        sandbox2.expires_at = datetime.now(UTC) + timedelta(hours=1)

        result = await sandbox_manager.cleanup_expired_sandboxes()

        assert result.cleaned_count == 1
        assert result.failed_count == 0
        assert sandbox1.sandbox_id in result.cleaned_sandbox_ids

        retrieved1 = await sandbox_manager.get_sandbox(sandbox1.sandbox_id)
        assert retrieved1 is None

        retrieved2 = await sandbox_manager.get_sandbox(sandbox2.sandbox_id)
        assert retrieved2 is not None


class TestMockSchemaManager:
    async def test_create_schema(self, schema_manager: MockSchemaManager) -> None:
        await schema_manager.create_schema("test_schema")
        exists = await schema_manager.schema_exists("test_schema")
        assert exists is True

    async def test_create_duplicate_schema(self, schema_manager: MockSchemaManager) -> None:
        await schema_manager.create_schema("test_schema")

        with pytest.raises(ValueError) as exc_info:
            await schema_manager.create_schema("test_schema")

        assert "already exists" in str(exc_info.value).lower()

    async def test_drop_schema(self, schema_manager: MockSchemaManager) -> None:
        await schema_manager.create_schema("test_schema")
        await schema_manager.drop_schema("test_schema")

        exists = await schema_manager.schema_exists("test_schema")
        assert exists is False

    async def test_seed_data(self, schema_manager: MockSchemaManager) -> None:
        await schema_manager.create_schema("test_schema")
        await schema_manager.seed_data("test_schema", lesson_id=5)

    async def test_seed_data_nonexistent_schema(self, schema_manager: MockSchemaManager) -> None:
        with pytest.raises(ValueError) as exc_info:
            await schema_manager.seed_data("nonexistent_schema", lesson_id=5)

        assert "does not exist" in str(exc_info.value).lower()

    async def test_create_sandbox_user(self, schema_manager: MockSchemaManager) -> None:
        await schema_manager.create_sandbox_user(
            username="test_user",
            password="test_pass",
            schema_name="test_schema",
        )

    async def test_drop_sandbox_user(self, schema_manager: MockSchemaManager) -> None:
        await schema_manager.create_sandbox_user(
            username="test_user",
            password="test_pass",
            schema_name="test_schema",
        )
        await schema_manager.drop_sandbox_user("test_user")


class TestMockQueryExecutor:
    async def test_execute_valid_query(
        self, query_executor: MockQueryExecutor, sandbox_manager: InMemorySandboxManager
    ) -> None:
        sandbox = await sandbox_manager.create_sandbox(user_id=1, lesson_id=5)
        sandbox.status = SandboxStatus.ACTIVE

        result = await query_executor.execute_query(sandbox, "SELECT * FROM employees")

        assert result.row_count > 0
        assert len(result.columns) > 0
        assert len(result.rows) == result.row_count

    async def test_execute_invalid_query(
        self, query_executor: MockQueryExecutor, sandbox_manager: InMemorySandboxManager
    ) -> None:
        sandbox = await sandbox_manager.create_sandbox(user_id=1, lesson_id=5)
        sandbox.status = SandboxStatus.ACTIVE

        with pytest.raises(ValueError) as exc_info:
            await query_executor.execute_query(sandbox, "DROP TABLE employees")

        assert "invalid query" in str(exc_info.value).lower()

    async def test_validate_query(self, query_executor: MockQueryExecutor) -> None:
        result = await query_executor.validate_query("SELECT * FROM employees")

        assert isinstance(result, QueryValidationResult)
        assert result.is_valid is True
        assert result.query_type == "SELECT"


class TestSandboxService:
    async def test_create_sandbox(self, sandbox_service: SandboxService) -> None:
        sandbox = await sandbox_service.create_sandbox(user_id=1, lesson_id=5)

        assert sandbox.sandbox_id is not None
        assert sandbox.user_id == 1
        assert sandbox.lesson_id == 5
        assert sandbox.status == SandboxStatus.ACTIVE

    async def test_create_sandbox_disabled(
        self,
        sandbox_manager: InMemorySandboxManager,
        schema_manager: MockSchemaManager,
        query_executor: MockQueryExecutor,
    ) -> None:
        disabled_config = SandboxConfig(enabled=False)
        service = SandboxService(
            config=disabled_config,
            sandbox_manager=sandbox_manager,
            schema_manager=schema_manager,
            query_executor=query_executor,
        )

        with pytest.raises(RuntimeError) as exc_info:
            await service.create_sandbox(user_id=1, lesson_id=5)

        assert "not enabled" in str(exc_info.value).lower()

    async def test_execute_query(self, sandbox_service: SandboxService) -> None:
        sandbox = await sandbox_service.create_sandbox(user_id=1, lesson_id=5)

        result = await sandbox_service.execute_query(
            sandbox.sandbox_id,
            "SELECT * FROM employees",
        )

        assert result.row_count >= 0
        assert isinstance(result.columns, list)
        assert isinstance(result.rows, list)

    async def test_execute_query_nonexistent_sandbox(self, sandbox_service: SandboxService) -> None:
        with pytest.raises(ValueError) as exc_info:
            await sandbox_service.execute_query("nonexistent_id", "SELECT * FROM employees")

        assert "not found" in str(exc_info.value).lower()

    async def test_execute_query_invalid_sql(self, sandbox_service: SandboxService) -> None:
        sandbox = await sandbox_service.create_sandbox(user_id=1, lesson_id=5)

        with pytest.raises(ValueError) as exc_info:
            await sandbox_service.execute_query(sandbox.sandbox_id, "DROP TABLE employees")

        assert "invalid query" in str(exc_info.value).lower()

    async def test_destroy_sandbox(self, sandbox_service: SandboxService) -> None:
        sandbox = await sandbox_service.create_sandbox(user_id=1, lesson_id=5)

        await sandbox_service.destroy_sandbox(sandbox.sandbox_id)

        retrieved = await sandbox_service.sandbox_manager.get_sandbox(sandbox.sandbox_id)
        assert retrieved is None

    async def test_destroy_nonexistent_sandbox(self, sandbox_service: SandboxService) -> None:
        with pytest.raises(ValueError) as exc_info:
            await sandbox_service.destroy_sandbox("nonexistent_id")

        assert "not found" in str(exc_info.value).lower()

    async def test_cleanup_expired(self, sandbox_service: SandboxService) -> None:
        result = await sandbox_service.cleanup_expired()

        assert result.cleaned_count >= 0
        assert result.failed_count >= 0
        assert isinstance(result.duration, float)
