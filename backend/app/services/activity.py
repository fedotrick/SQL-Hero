from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import ActivityLog, ActivityType, User


async def log_activity(
    db: AsyncSession,
    user_id: int,
    activity_type: ActivityType,
    entity_id: int | None = None,
    entity_type: str | None = None,
    details: str | None = None,
) -> ActivityLog:
    """
    Log an activity to the activity log.

    Args:
        db: Database session
        user_id: ID of the user performing the activity
        activity_type: Type of activity being logged
        entity_id: Optional ID of related entity (e.g., lesson_id)
        entity_type: Optional type of entity (e.g., "lesson", "module")
        details: Optional additional details about the activity

    Returns:
        ActivityLog: The created activity log entry
    """
    activity = ActivityLog(
        user_id=user_id,
        activity_type=activity_type,
        entity_id=entity_id,
        entity_type=entity_type,
        details=details,
        created_at=datetime.utcnow(),
    )
    db.add(activity)
    await db.flush()
    return activity


async def get_activity_heatmap(
    db: AsyncSession,
    user: User,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[dict[str, Any]]:
    """
    Get activity heatmap data grouped by date.

    Returns daily activity counts for visualization in a heatmap/calendar view.
    Uses efficient GROUP BY date query with proper indexing.

    Args:
        db: Database session
        user: User to get heatmap for
        start_date: Optional start date (defaults to 365 days ago)
        end_date: Optional end date (defaults to today)

    Returns:
        list[dict]: List of {"date": "YYYY-MM-DD", "count": int} entries
    """
    if end_date is None:
        end_date = date.today()

    if start_date is None:
        start_date = end_date - timedelta(days=365)

    # Convert dates to datetime for comparison
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())

    # Query activity log grouped by date
    # Using DATE(created_at) to bucket activities by date
    query = (
        select(
            func.date(ActivityLog.created_at).label("activity_date"),
            func.count(ActivityLog.id).label("count"),
        )
        .where(
            ActivityLog.user_id == user.id,
            ActivityLog.created_at >= start_datetime,
            ActivityLog.created_at <= end_datetime,
        )
        .group_by(func.date(ActivityLog.created_at))
        .order_by(func.date(ActivityLog.created_at))
    )

    result = await db.execute(query)
    rows = result.all()

    # Format results
    heatmap_data = [{"date": str(row.activity_date), "count": row.count} for row in rows]

    return heatmap_data


async def get_daily_activity_stats(
    db: AsyncSession,
    user: User,
    target_date: date | None = None,
) -> dict[str, Any]:
    """
    Get detailed activity stats for a specific day.

    Args:
        db: Database session
        user: User to get stats for
        target_date: Date to get stats for (defaults to today)

    Returns:
        dict: Daily statistics including activity counts by type
    """
    if target_date is None:
        target_date = date.today()

    # Convert to datetime range
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())

    # Get total count for the day
    total_query = select(func.count(ActivityLog.id)).where(
        ActivityLog.user_id == user.id,
        ActivityLog.created_at >= start_datetime,
        ActivityLog.created_at <= end_datetime,
    )
    total_result = await db.execute(total_query)
    total_count = total_result.scalar_one()

    # Get counts by activity type
    by_type_query = (
        select(
            ActivityLog.activity_type,
            func.count(ActivityLog.id).label("count"),
        )
        .where(
            ActivityLog.user_id == user.id,
            ActivityLog.created_at >= start_datetime,
            ActivityLog.created_at <= end_datetime,
        )
        .group_by(ActivityLog.activity_type)
    )
    by_type_result = await db.execute(by_type_query)
    by_type_rows = by_type_result.all()

    # Format activity type counts
    activity_by_type = {row.activity_type.value: row.count for row in by_type_rows}

    return {
        "date": str(target_date),
        "total_count": total_count,
        "activity_by_type": activity_by_type,
    }


async def get_streak_data(db: AsyncSession, user: User) -> dict[str, Any]:
    """
    Get streak information for a user.

    Calculates streak continuity by analyzing daily activity patterns.
    Returns current streak, longest streak, and activity dates.

    Args:
        db: Database session
        user: User to get streak data for

    Returns:
        dict: Streak statistics and activity dates
    """
    # Get all unique activity dates for the user
    query = (
        select(func.date(ActivityLog.created_at).label("activity_date"))
        .where(ActivityLog.user_id == user.id)
        .group_by(func.date(ActivityLog.created_at))
        .order_by(func.date(ActivityLog.created_at).desc())
    )

    result = await db.execute(query)
    activity_dates = [row.activity_date for row in result.all()]

    if not activity_dates:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "total_active_days": 0,
            "last_active_date": None,
            "streak_start_date": None,
        }

    # Calculate current streak
    today = date.today()
    current_streak = 0
    streak_start_date = None

    # Check if user was active today or yesterday to have an active streak
    if activity_dates[0] >= today - timedelta(days=1):
        current_streak = 1
        streak_start_date = activity_dates[0]

        # Count consecutive days backwards
        for i in range(1, len(activity_dates)):
            expected_date = activity_dates[i - 1] - timedelta(days=1)
            if activity_dates[i] == expected_date:
                current_streak += 1
                streak_start_date = activity_dates[i]
            else:
                break

    # Calculate longest streak in history
    longest_streak = 0
    temp_streak = 1

    for i in range(1, len(activity_dates)):
        expected_date = activity_dates[i - 1] - timedelta(days=1)
        if activity_dates[i] == expected_date:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 1

    # Account for single-day streaks
    longest_streak = max(longest_streak, 1) if activity_dates else 0

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_active_days": len(activity_dates),
        "last_active_date": str(activity_dates[0]) if activity_dates else None,
        "streak_start_date": str(streak_start_date) if streak_start_date else None,
    }
