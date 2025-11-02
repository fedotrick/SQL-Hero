from datetime import date

from pydantic import BaseModel, Field


class ActivityHeatmapEntry(BaseModel):
    """Single entry in the activity heatmap."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    count: int = Field(..., description="Number of activities on this date", ge=0)


class ActivityHeatmapResponse(BaseModel):
    """Response containing heatmap data for calendar visualization."""

    user_id: int = Field(..., description="ID of the user")
    start_date: str = Field(..., description="Start date of the heatmap range (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date of the heatmap range (YYYY-MM-DD)")
    data: list[ActivityHeatmapEntry] = Field(..., description="List of daily activity counts")
    total_activities: int = Field(..., description="Total number of activities in range", ge=0)


class DailyActivityStats(BaseModel):
    """Detailed activity statistics for a specific day."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    total_count: int = Field(..., description="Total activities for the day", ge=0)
    activity_by_type: dict[str, int] = Field(..., description="Activity counts grouped by type")


class StreakData(BaseModel):
    """User streak information and activity patterns."""

    current_streak: int = Field(..., description="Current consecutive days streak", ge=0)
    longest_streak: int = Field(..., description="Longest streak ever achieved", ge=0)
    total_active_days: int = Field(..., description="Total number of active days", ge=0)
    last_active_date: str | None = Field(None, description="Last activity date (YYYY-MM-DD)")
    streak_start_date: str | None = Field(
        None, description="Start date of current streak (YYYY-MM-DD)"
    )


class ActivityCalendarResponse(BaseModel):
    """Combined response with heatmap and streak data."""

    heatmap: ActivityHeatmapResponse = Field(..., description="Activity heatmap data")
    streak: StreakData = Field(..., description="Streak statistics")
