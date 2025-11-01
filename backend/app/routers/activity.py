from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.database import User
from app.schemas.activity import (
    ActivityCalendarResponse,
    ActivityHeatmapResponse,
    DailyActivityStats,
    StreakData,
)
from app.services.activity import (
    get_activity_heatmap,
    get_daily_activity_stats,
    get_streak_data,
)

router = APIRouter(prefix="/activity", tags=["activity"])


@router.get(
    "/heatmap",
    response_model=ActivityHeatmapResponse,
    summary="Get activity heatmap data",
    description=(
        "Get activity heatmap data for calendar visualization. "
        "Returns daily activity counts grouped by date. "
        "Efficient queries with GROUP BY date and proper indexing."
    ),
)
async def get_heatmap(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    start_date: Annotated[
        date | None,
        Query(description="Start date (YYYY-MM-DD). Defaults to 365 days ago"),
    ] = None,
    end_date: Annotated[
        date | None,
        Query(description="End date (YYYY-MM-DD). Defaults to today"),
    ] = None,
) -> ActivityHeatmapResponse:
    """
    Get activity heatmap data for the authenticated user.

    Returns daily activity counts for visualization in a calendar/heatmap view.
    Uses efficient GROUP BY date queries with indexes on (user_id, created_at).

    Query parameters:
    - start_date: Optional start date (defaults to 365 days ago)
    - end_date: Optional end date (defaults to today)

    Returns:
    - List of {"date": "YYYY-MM-DD", "count": int} entries
    - Date range information
    - Total activity count
    """
    if end_date is None:
        end_date = date.today()

    if start_date is None:
        start_date = end_date - timedelta(days=365)

    heatmap_data = await get_activity_heatmap(db, current_user, start_date, end_date)

    total_activities = sum(entry["count"] for entry in heatmap_data)

    return ActivityHeatmapResponse(
        user_id=current_user.id,
        start_date=str(start_date),
        end_date=str(end_date),
        data=heatmap_data,
        total_activities=total_activities,
    )


@router.get(
    "/daily",
    response_model=DailyActivityStats,
    summary="Get daily activity statistics",
    description=(
        "Get detailed activity statistics for a specific day. "
        "Includes total count and breakdown by activity type."
    ),
)
async def get_daily_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    target_date: Annotated[
        date | None,
        Query(description="Target date (YYYY-MM-DD). Defaults to today"),
    ] = None,
) -> DailyActivityStats:
    """
    Get detailed activity statistics for a specific day.

    Returns:
    - Total activity count for the day
    - Activity counts grouped by type (lesson_completed, challenge_attempted, etc.)
    - Date information
    """
    stats = await get_daily_activity_stats(db, current_user, target_date)
    return DailyActivityStats(**stats)


@router.get(
    "/streak",
    response_model=StreakData,
    summary="Get streak information",
    description=(
        "Get current and longest streak data for the user. "
        "Calculates streak continuity by analyzing daily activity patterns."
    ),
)
async def get_streak(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StreakData:
    """
    Get streak information for the authenticated user.

    Calculates:
    - Current consecutive days streak
    - Longest streak ever achieved
    - Total active days
    - Last activity date
    - Current streak start date

    Returns:
    - Comprehensive streak statistics
    """
    streak_data = await get_streak_data(db, current_user)
    return StreakData(**streak_data)


@router.get(
    "/calendar",
    response_model=ActivityCalendarResponse,
    summary="Get combined calendar and streak data",
    description=(
        "Get both activity heatmap and streak data in a single request. "
        "Optimized for displaying activity calendar with streak information."
    ),
)
async def get_calendar(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    start_date: Annotated[
        date | None,
        Query(description="Start date (YYYY-MM-DD). Defaults to 365 days ago"),
    ] = None,
    end_date: Annotated[
        date | None,
        Query(description="End date (YYYY-MM-DD). Defaults to today"),
    ] = None,
) -> ActivityCalendarResponse:
    """
    Get combined activity calendar data including heatmap and streak info.

    This endpoint combines heatmap and streak data in a single request,
    which is ideal for dashboard/calendar views that need both pieces of information.

    Returns:
    - Activity heatmap with daily counts
    - Current and longest streak
    - Total active days
    - Date range information
    """
    if end_date is None:
        end_date = date.today()

    if start_date is None:
        start_date = end_date - timedelta(days=365)

    # Fetch both heatmap and streak data
    heatmap_data = await get_activity_heatmap(db, current_user, start_date, end_date)
    streak_data = await get_streak_data(db, current_user)

    total_activities = sum(entry["count"] for entry in heatmap_data)

    heatmap_response = ActivityHeatmapResponse(
        user_id=current_user.id,
        start_date=str(start_date),
        end_date=str(end_date),
        data=heatmap_data,
        total_activities=total_activities,
    )

    return ActivityCalendarResponse(
        heatmap=heatmap_response,
        streak=StreakData(**streak_data),
    )
