import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.fixture(scope="module")
def sync_engine():
    engine = create_engine(
        "mysql+pymysql://user:password@localhost:3306/appdb",
        echo=False,
    )
    yield engine
    engine.dispose()


@pytest.fixture(scope="module")
async def test_engine():
    engine = create_async_engine(
        "mysql+aiomysql://user:password@localhost:3306/appdb",
        echo=False,
    )
    yield engine
    await engine.dispose()


@pytest.fixture
def alembic_config():
    config = Config("alembic.ini")
    return config


class TestMigrations:
    def test_alembic_config_exists(self, alembic_config):
        assert alembic_config is not None
        assert alembic_config.get_main_option("script_location") == "alembic"

    def test_downgrade_to_base(self, alembic_config, sync_engine):
        command.downgrade(alembic_config, "base")

        inspector = inspect(sync_engine)
        tables = inspector.get_table_names()
        assert "users" not in tables
        assert "modules" not in tables
        assert "lessons" not in tables
        assert "user_progress" not in tables
        assert "achievements" not in tables
        assert "user_achievements" not in tables
        assert "leaderboard_cache" not in tables
        assert "activity_log" not in tables

    def test_upgrade_to_head(self, alembic_config, sync_engine):
        command.upgrade(alembic_config, "head")

        inspector = inspect(sync_engine)
        tables = inspector.get_table_names()
        assert "users" in tables
        assert "modules" in tables
        assert "lessons" in tables
        assert "user_progress" in tables
        assert "achievements" in tables
        assert "user_achievements" in tables
        assert "leaderboard_cache" in tables
        assert "activity_log" in tables

    def test_schema_after_upgrade(self, sync_engine):
        inspector = inspect(sync_engine)

        users_columns = {
            col["name"]: col for col in inspector.get_columns("users")
        }
        assert "telegram_id" in users_columns
        assert "username" in users_columns
        assert "is_active" in users_columns

        modules_columns = {
            col["name"]: col for col in inspector.get_columns("modules")
        }
        assert "title" in modules_columns
        assert "order" in modules_columns
        assert "is_published" in modules_columns

        lessons_columns = {
            col["name"]: col for col in inspector.get_columns("lessons")
        }
        assert "module_id" in lessons_columns
        assert "title" in lessons_columns
        assert "content" in lessons_columns
        assert "order" in lessons_columns

    def test_foreign_keys_exist(self, sync_engine):
        inspector = inspect(sync_engine)

        lessons_fks = inspector.get_foreign_keys("lessons")
        assert len(lessons_fks) > 0
        assert any(fk["referred_table"] == "modules" for fk in lessons_fks)

        user_progress_fks = inspector.get_foreign_keys("user_progress")
        assert len(user_progress_fks) >= 2
        assert any(fk["referred_table"] == "users" for fk in user_progress_fks)
        assert any(fk["referred_table"] == "lessons" for fk in user_progress_fks)

        activity_log_fks = inspector.get_foreign_keys("activity_log")
        assert len(activity_log_fks) > 0
        assert any(fk["referred_table"] == "users" for fk in activity_log_fks)

    def test_indexes_exist_after_upgrade(self, sync_engine):
        inspector = inspect(sync_engine)

        users_indexes = inspector.get_indexes("users")
        telegram_id_index = next(
            (idx for idx in users_indexes if "telegram_id" in idx["column_names"]),
            None,
        )
        assert telegram_id_index is not None
        assert telegram_id_index["unique"] is True

        activity_log_indexes = inspector.get_indexes("activity_log")
        created_at_indexes = [
            idx
            for idx in activity_log_indexes
            if "created_at" in idx["column_names"]
        ]
        assert len(created_at_indexes) > 0

        user_progress_indexes = inspector.get_indexes("user_progress")
        composite_indexes = [
            idx
            for idx in user_progress_indexes
            if len(idx["column_names"]) > 1
        ]
        assert len(composite_indexes) > 0

    def test_unique_constraints_exist(self, sync_engine):
        inspector = inspect(sync_engine)

        user_progress_constraints = inspector.get_unique_constraints(
            "user_progress"
        )
        assert len(user_progress_constraints) > 0

        user_achievements_constraints = inspector.get_unique_constraints(
            "user_achievements"
        )
        assert len(user_achievements_constraints) > 0

    def test_downgrade_and_upgrade_cycle(self, alembic_config, sync_engine):
        command.downgrade(alembic_config, "base")

        inspector = inspect(sync_engine)
        tables_after_downgrade = inspector.get_table_names()
        assert "users" not in tables_after_downgrade

        command.upgrade(alembic_config, "head")

        inspector = inspect(sync_engine)
        tables_after_upgrade = inspector.get_table_names()
        assert "users" in tables_after_upgrade
        assert "modules" in tables_after_upgrade
        assert "lessons" in tables_after_upgrade
        assert "user_progress" in tables_after_upgrade
        assert "achievements" in tables_after_upgrade
        assert "user_achievements" in tables_after_upgrade
        assert "leaderboard_cache" in tables_after_upgrade
        assert "activity_log" in tables_after_upgrade

    def test_alembic_version_table_exists(self, sync_engine):
        inspector = inspect(sync_engine)
        tables = inspector.get_table_names()
        assert "alembic_version" in tables

    async def test_current_revision_not_empty(self, test_engine):
        async with test_engine.connect() as conn:
            result = await conn.execute(
                text("SELECT version_num FROM alembic_version")
            )
            row = result.fetchone()
            assert row is not None
            assert row[0] is not None
