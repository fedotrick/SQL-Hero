import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import (
    Achievement,
    AchievementType,
    ActivityLog,
    ActivityType,
    Base,
    Lesson,
    LeaderboardCache,
    Module,
    ProgressStatus,
    User,
    UserAchievement,
    UserProgress,
)


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
async def session(test_engine):
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


class TestUserModel:
    async def test_user_tablename(self):
        assert User.__tablename__ == "users"

    async def test_user_columns(self):
        assert hasattr(User, "id")
        assert hasattr(User, "telegram_id")
        assert hasattr(User, "username")
        assert hasattr(User, "first_name")
        assert hasattr(User, "last_name")
        assert hasattr(User, "language_code")
        assert hasattr(User, "is_active")
        assert hasattr(User, "created_at")
        assert hasattr(User, "updated_at")

    async def test_user_relationships(self):
        assert hasattr(User, "progress")
        assert hasattr(User, "user_achievements")
        assert hasattr(User, "activity_logs")

    def test_user_telegram_id_unique(self, sync_engine):
        inspector = inspect(sync_engine)
        indexes = inspector.get_indexes("users")
        telegram_id_index = next(
            (idx for idx in indexes if "telegram_id" in idx["column_names"]),
            None,
        )
        assert telegram_id_index is not None
        assert telegram_id_index["unique"] is True


class TestModuleModel:
    async def test_module_tablename(self):
        assert Module.__tablename__ == "modules"

    async def test_module_columns(self):
        assert hasattr(Module, "id")
        assert hasattr(Module, "title")
        assert hasattr(Module, "description")
        assert hasattr(Module, "order")
        assert hasattr(Module, "is_published")
        assert hasattr(Module, "created_at")
        assert hasattr(Module, "updated_at")

    async def test_module_relationships(self):
        assert hasattr(Module, "lessons")

    def test_module_order_index(self, sync_engine):
        inspector = inspect(sync_engine)
        indexes = inspector.get_indexes("modules")
        order_index = next(
            (idx for idx in indexes if "order" in idx["column_names"]),
            None,
        )
        assert order_index is not None


class TestLessonModel:
    async def test_lesson_tablename(self):
        assert Lesson.__tablename__ == "lessons"

    async def test_lesson_columns(self):
        assert hasattr(Lesson, "id")
        assert hasattr(Lesson, "module_id")
        assert hasattr(Lesson, "title")
        assert hasattr(Lesson, "content")
        assert hasattr(Lesson, "order")
        assert hasattr(Lesson, "estimated_duration")
        assert hasattr(Lesson, "is_published")
        assert hasattr(Lesson, "created_at")
        assert hasattr(Lesson, "updated_at")

    async def test_lesson_relationships(self):
        assert hasattr(Lesson, "module")
        assert hasattr(Lesson, "progress")

    def test_lesson_composite_index(self, sync_engine):
        inspector = inspect(sync_engine)
        indexes = inspector.get_indexes("lessons")
        module_order_index = next(
            (
                idx
                for idx in indexes
                if "module_id" in idx["column_names"]
                and "order" in idx["column_names"]
            ),
            None,
        )
        assert module_order_index is not None


class TestUserProgressModel:
    async def test_user_progress_tablename(self):
        assert UserProgress.__tablename__ == "user_progress"

    async def test_user_progress_columns(self):
        assert hasattr(UserProgress, "id")
        assert hasattr(UserProgress, "user_id")
        assert hasattr(UserProgress, "lesson_id")
        assert hasattr(UserProgress, "status")
        assert hasattr(UserProgress, "score")
        assert hasattr(UserProgress, "attempts")
        assert hasattr(UserProgress, "started_at")
        assert hasattr(UserProgress, "completed_at")
        assert hasattr(UserProgress, "created_at")
        assert hasattr(UserProgress, "updated_at")

    async def test_user_progress_relationships(self):
        assert hasattr(UserProgress, "user")
        assert hasattr(UserProgress, "lesson")

    def test_user_progress_unique_constraint(self, sync_engine):
        inspector = inspect(sync_engine)
        constraints = inspector.get_unique_constraints("user_progress")
        user_lesson_constraint = next(
            (c for c in constraints if "user_id" in c["column_names"]), None
        )
        assert user_lesson_constraint is not None
        assert "lesson_id" in user_lesson_constraint["column_names"]

    def test_user_progress_composite_indexes(self, sync_engine):
        inspector = inspect(sync_engine)
        indexes = inspector.get_indexes("user_progress")
        user_status_index = next(
            (
                idx
                for idx in indexes
                if "user_id" in idx["column_names"]
                and "status" in idx["column_names"]
            ),
            None,
        )
        assert user_status_index is not None


class TestAchievementModel:
    async def test_achievement_tablename(self):
        assert Achievement.__tablename__ == "achievements"

    async def test_achievement_columns(self):
        assert hasattr(Achievement, "id")
        assert hasattr(Achievement, "type")
        assert hasattr(Achievement, "title")
        assert hasattr(Achievement, "description")
        assert hasattr(Achievement, "icon")
        assert hasattr(Achievement, "points")
        assert hasattr(Achievement, "criteria")
        assert hasattr(Achievement, "created_at")

    async def test_achievement_relationships(self):
        assert hasattr(Achievement, "user_achievements")

    async def test_achievement_type_enum(self):
        assert hasattr(AchievementType, "LESSON_COMPLETED")
        assert hasattr(AchievementType, "MODULE_COMPLETED")
        assert hasattr(AchievementType, "STREAK")
        assert hasattr(AchievementType, "CHALLENGES_SOLVED")
        assert hasattr(AchievementType, "MILESTONE")


class TestUserAchievementModel:
    async def test_user_achievement_tablename(self):
        assert UserAchievement.__tablename__ == "user_achievements"

    async def test_user_achievement_columns(self):
        assert hasattr(UserAchievement, "id")
        assert hasattr(UserAchievement, "user_id")
        assert hasattr(UserAchievement, "achievement_id")
        assert hasattr(UserAchievement, "earned_at")

    async def test_user_achievement_relationships(self):
        assert hasattr(UserAchievement, "user")
        assert hasattr(UserAchievement, "achievement")

    def test_user_achievement_unique_constraint(self, sync_engine):
        inspector = inspect(sync_engine)
        constraints = inspector.get_unique_constraints("user_achievements")
        user_achievement_constraint = next(
            (c for c in constraints if "user_id" in c["column_names"]), None
        )
        assert user_achievement_constraint is not None
        assert "achievement_id" in user_achievement_constraint["column_names"]


class TestLeaderboardCacheModel:
    async def test_leaderboard_cache_tablename(self):
        assert LeaderboardCache.__tablename__ == "leaderboard_cache"

    async def test_leaderboard_cache_columns(self):
        assert hasattr(LeaderboardCache, "id")
        assert hasattr(LeaderboardCache, "user_id")
        assert hasattr(LeaderboardCache, "rank")
        assert hasattr(LeaderboardCache, "total_score")
        assert hasattr(LeaderboardCache, "lessons_completed")
        assert hasattr(LeaderboardCache, "achievements_count")
        assert hasattr(LeaderboardCache, "updated_at")

    def test_leaderboard_cache_rank_index(self, sync_engine):
        inspector = inspect(sync_engine)
        indexes = inspector.get_indexes("leaderboard_cache")
        rank_score_index = next(
            (
                idx
                for idx in indexes
                if "rank" in idx["column_names"]
                and "total_score" in idx["column_names"]
            ),
            None,
        )
        assert rank_score_index is not None


class TestActivityLogModel:
    async def test_activity_log_tablename(self):
        assert ActivityLog.__tablename__ == "activity_log"

    async def test_activity_log_columns(self):
        assert hasattr(ActivityLog, "id")
        assert hasattr(ActivityLog, "user_id")
        assert hasattr(ActivityLog, "activity_type")
        assert hasattr(ActivityLog, "entity_id")
        assert hasattr(ActivityLog, "entity_type")
        assert hasattr(ActivityLog, "details")
        assert hasattr(ActivityLog, "created_at")

    async def test_activity_log_relationships(self):
        assert hasattr(ActivityLog, "user")

    def test_activity_log_date_index(self, sync_engine):
        inspector = inspect(sync_engine)
        indexes = inspector.get_indexes("activity_log")
        created_at_index = next(
            (idx for idx in indexes if idx["column_names"] == ["created_at"]),
            None,
        )
        assert created_at_index is not None

    def test_activity_log_composite_index(self, sync_engine):
        inspector = inspect(sync_engine)
        indexes = inspector.get_indexes("activity_log")
        composite_index = next(
            (
                idx
                for idx in indexes
                if "user_id" in idx["column_names"]
                and "activity_type" in idx["column_names"]
                and "created_at" in idx["column_names"]
            ),
            None,
        )
        assert composite_index is not None

    async def test_activity_type_enum(self):
        assert hasattr(ActivityType, "LESSON_STARTED")
        assert hasattr(ActivityType, "LESSON_COMPLETED")
        assert hasattr(ActivityType, "CHALLENGE_ATTEMPTED")
        assert hasattr(ActivityType, "CHALLENGE_SOLVED")
        assert hasattr(ActivityType, "ACHIEVEMENT_EARNED")
        assert hasattr(ActivityType, "LOGIN")


class TestProgressStatusEnum:
    def test_progress_status_values(self):
        assert hasattr(ProgressStatus, "NOT_STARTED")
        assert hasattr(ProgressStatus, "IN_PROGRESS")
        assert hasattr(ProgressStatus, "COMPLETED")


class TestModelConstraints:
    def test_user_not_null_constraints(self, sync_engine):
        inspector = inspect(sync_engine)
        columns = {col["name"]: col for col in inspector.get_columns("users")}
        assert columns["telegram_id"]["nullable"] is False
        assert columns["is_active"]["nullable"] is False
        assert columns["created_at"]["nullable"] is False
        assert columns["updated_at"]["nullable"] is False

    def test_module_not_null_constraints(self, sync_engine):
        inspector = inspect(sync_engine)
        columns = {col["name"]: col for col in inspector.get_columns("modules")}
        assert columns["title"]["nullable"] is False
        assert columns["order"]["nullable"] is False
        assert columns["is_published"]["nullable"] is False

    def test_lesson_not_null_constraints(self, sync_engine):
        inspector = inspect(sync_engine)
        columns = {col["name"]: col for col in inspector.get_columns("lessons")}
        assert columns["module_id"]["nullable"] is False
        assert columns["title"]["nullable"] is False
        assert columns["order"]["nullable"] is False

    def test_user_progress_not_null_constraints(self, sync_engine):
        inspector = inspect(sync_engine)
        columns = {
            col["name"]: col for col in inspector.get_columns("user_progress")
        }
        assert columns["user_id"]["nullable"] is False
        assert columns["lesson_id"]["nullable"] is False
        assert columns["status"]["nullable"] is False
        assert columns["attempts"]["nullable"] is False

    def test_achievement_not_null_constraints(self, sync_engine):
        inspector = inspect(sync_engine)
        columns = {
            col["name"]: col for col in inspector.get_columns("achievements")
        }
        assert columns["type"]["nullable"] is False
        assert columns["title"]["nullable"] is False
        assert columns["points"]["nullable"] is False

    def test_activity_log_not_null_constraints(self, sync_engine):
        inspector = inspect(sync_engine)
        columns = {
            col["name"]: col for col in inspector.get_columns("activity_log")
        }
        assert columns["user_id"]["nullable"] is False
        assert columns["activity_type"]["nullable"] is False
        assert columns["created_at"]["nullable"] is False
