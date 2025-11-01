from datetime import datetime

from pydantic import BaseModel, Field


class LeaderboardEntry(BaseModel):
    user_id: int
    username: str | None
    first_name: str | None
    rank: int
    xp: int
    level: int
    lessons_completed: int
    achievements_count: int


class LeaderboardResponse(BaseModel):
    entries: list[LeaderboardEntry]
    current_user: LeaderboardEntry | None = Field(
        None, description="Current user entry if not in top N"
    )
    last_updated: datetime | None = Field(None, description="Last cache refresh time")
    total_users: int = Field(0, description="Total number of users in leaderboard")


class RefreshLeaderboardResponse(BaseModel):
    success: bool
    message: str
    entries_updated: int
    timestamp: datetime
