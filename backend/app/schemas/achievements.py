from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AchievementBase(BaseModel):
    code: str
    type: str
    title: str
    description: str | None = None
    icon: str | None = None
    points: int
    criteria: str | None = None


class Achievement(AchievementBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AchievementProgress(BaseModel):
    current: int
    target: int
    percentage: float


class AchievementWithStatus(Achievement):
    is_earned: bool
    earned_at: datetime | None = None
    progress: AchievementProgress | None = None


class AchievementsListResponse(BaseModel):
    achievements: list[AchievementWithStatus]
    total_earned: int
    total_points: int


class AchievementUnlockedNotification(BaseModel):
    achievement_id: int
    achievement_code: str
    title: str
    description: str | None
    icon: str | None
    points: int
