import enum
from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProgressStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class AchievementType(enum.Enum):
    LESSON_COMPLETED = "lesson_completed"
    MODULE_COMPLETED = "module_completed"
    STREAK = "streak"
    CHALLENGES_SOLVED = "challenges_solved"
    MILESTONE = "milestone"


class ActivityType(enum.Enum):
    LESSON_STARTED = "lesson_started"
    LESSON_COMPLETED = "lesson_completed"
    CHALLENGE_ATTEMPTED = "challenge_attempted"
    CHALLENGE_SOLVED = "challenge_solved"
    ACHIEVEMENT_EARNED = "achievement_earned"
    LOGIN = "login"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_queries: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_active_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    progress: Mapped[list["UserProgress"]] = relationship(
        "UserProgress", back_populates="user", cascade="all, delete-orphan"
    )
    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="user", cascade="all, delete-orphan"
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        "ActivityLog", back_populates="user", cascade="all, delete-orphan"
    )


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    is_published: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson", back_populates="module", cascade="all, delete-orphan"
    )


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    theory: Mapped[str | None] = mapped_column(Text, nullable=True)
    sql_solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_published: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    module: Mapped["Module"] = relationship("Module", back_populates="lessons")
    progress: Mapped[list["UserProgress"]] = relationship(
        "UserProgress", back_populates="lesson", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("idx_module_order", "module_id", "order"),)


class UserProgress(Base):
    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id"), nullable=False)
    status: Mapped[ProgressStatus] = mapped_column(
        Enum(ProgressStatus), default=ProgressStatus.NOT_STARTED, nullable=False
    )
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    first_try: Mapped[bool | None] = mapped_column(nullable=True)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="progress")
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="progress")

    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson"),
        Index("idx_user_status", "user_id", "status"),
        Index("idx_lesson_status", "lesson_id", "status"),
    )


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    type: Mapped[AchievementType] = mapped_column(Enum(AchievementType), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="achievement", cascade="all, delete-orphan"
    )


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    achievement_id: Mapped[int] = mapped_column(ForeignKey("achievements.id"), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="user_achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement", back_populates="user_achievements")

    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
        Index("idx_user_earned", "user_id", "earned_at"),
    )


class LeaderboardCache(Base):
    __tablename__ = "leaderboard_cache"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    total_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lessons_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    achievements_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (Index("idx_rank_score", "rank", "total_score"),)


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    activity_type: Mapped[ActivityType] = mapped_column(Enum(ActivityType), nullable=False, index=True)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    user: Mapped["User"] = relationship("User", back_populates="activity_logs")

    __table_args__ = (
        Index("idx_user_activity_date", "user_id", "activity_type", "created_at"),
        Index("idx_created_at", "created_at"),
    )
