from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LessonAttemptRequest(BaseModel):
    """Request body for submitting a lesson attempt."""

    user_query: str = Field(..., description="SQL query submitted by user")
    success: bool = Field(..., description="Whether the query matched expected result")


class AchievementUnlocked(BaseModel):
    """Achievement that was just unlocked."""

    achievement_id: int
    code: str
    title: str
    icon: str | None
    points: int


class LessonAttemptResponse(BaseModel):
    """Response after submitting a lesson attempt."""

    success: bool
    xp_earned: int
    total_xp: int
    level: int
    level_up: bool
    current_streak: int
    longest_streak: int
    attempts: int
    first_try: bool
    progress_status: str
    message: str
    achievements_unlocked: list[AchievementUnlocked] = []


class UserProgressSummary(BaseModel):
    """Summary of user's overall progress for dashboard."""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str | None
    xp: int
    level: int
    xp_to_next_level: int
    current_level_xp: int
    next_level_xp: int
    progress_percentage: float
    current_streak: int
    longest_streak: int
    total_queries: int
    lessons_completed: int
    total_lessons: int
    modules_completed: int
    total_modules: int
    achievements_count: int
    last_active_date: datetime | None
