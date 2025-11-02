from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import (
    LeaderboardCache,
    ProgressStatus,
    User,
    UserAchievement,
    UserProgress,
)
from app.schemas.leaderboard import LeaderboardEntry


async def refresh_leaderboard_cache(db: AsyncSession) -> int:
    """
    Refresh the leaderboard cache from users' XP data.
    This operation is concurrency-safe using database transactions.

    Returns:
        int: Number of entries updated/created
    """
    # Get all active users with their stats
    users_query = (
        select(
            User.id,
            User.xp,
            User.level,
            User.username,
            User.first_name,
            func.count(UserProgress.id.distinct()).label("lessons_completed"),
            func.count(UserAchievement.id.distinct()).label("achievements_count"),
        )
        .outerjoin(
            UserProgress,
            (UserProgress.user_id == User.id) & (UserProgress.status == ProgressStatus.COMPLETED),
        )
        .outerjoin(UserAchievement, UserAchievement.user_id == User.id)
        .where(User.is_active == True)  # noqa: E712
        .group_by(User.id)
        .order_by(User.xp.desc(), User.id.asc())
    )

    result = await db.execute(users_query)
    users_data = result.all()

    # Clear existing cache within the same transaction
    await db.execute(delete(LeaderboardCache))

    # Build new cache entries with ranks
    cache_entries = []
    for rank, user_data in enumerate(users_data, start=1):
        cache_entry = LeaderboardCache(
            user_id=user_data.id,
            rank=rank,
            total_score=user_data.xp,
            lessons_completed=user_data.lessons_completed,
            achievements_count=user_data.achievements_count,
            updated_at=datetime.utcnow(),
        )
        cache_entries.append(cache_entry)

    # Bulk insert new cache entries
    db.add_all(cache_entries)
    await db.commit()

    return len(cache_entries)


async def get_leaderboard(db: AsyncSession, limit: int = 100, user_id: int | None = None) -> dict:
    """
    Get the top N users from the leaderboard cache, plus the current user's rank if not in top N.

    Args:
        db: Database session
        limit: Number of top users to return (default 100)
        user_id: Current user ID to include their rank even if not in top N

    Returns:
        dict: Dictionary with entries, current_user, last_updated, and total_users
    """
    # Get top N entries with user data
    top_query = (
        select(
            LeaderboardCache.user_id,
            LeaderboardCache.rank,
            LeaderboardCache.total_score,
            LeaderboardCache.lessons_completed,
            LeaderboardCache.achievements_count,
            LeaderboardCache.updated_at,
            User.username,
            User.first_name,
            User.level,
        )
        .join(User, User.id == LeaderboardCache.user_id)
        .order_by(LeaderboardCache.rank.asc())
        .limit(limit)
    )

    result = await db.execute(top_query)
    top_entries = result.all()

    # Get total count
    count_query = select(func.count(LeaderboardCache.id))
    count_result = await db.execute(count_query)
    total_users = count_result.scalar_one()

    # Build response entries
    entries = [
        LeaderboardEntry(
            user_id=entry.user_id,
            username=entry.username,
            first_name=entry.first_name,
            rank=entry.rank,
            xp=entry.total_score,
            level=entry.level,
            lessons_completed=entry.lessons_completed,
            achievements_count=entry.achievements_count,
        )
        for entry in top_entries
    ]

    # Get last updated timestamp
    last_updated = top_entries[0].updated_at if top_entries else None

    # Check if current user is in top N
    current_user_entry = None
    if user_id:
        user_in_top = any(entry.user_id == user_id for entry in top_entries)

        # If user is not in top N, fetch their entry
        if not user_in_top:
            user_query = (
                select(
                    LeaderboardCache.user_id,
                    LeaderboardCache.rank,
                    LeaderboardCache.total_score,
                    LeaderboardCache.lessons_completed,
                    LeaderboardCache.achievements_count,
                    User.username,
                    User.first_name,
                    User.level,
                )
                .join(User, User.id == LeaderboardCache.user_id)
                .where(LeaderboardCache.user_id == user_id)
            )

            user_result = await db.execute(user_query)
            user_data = user_result.first()

            if user_data:
                current_user_entry = LeaderboardEntry(
                    user_id=user_data.user_id,
                    username=user_data.username,
                    first_name=user_data.first_name,
                    rank=user_data.rank,
                    xp=user_data.total_score,
                    level=user_data.level,
                    lessons_completed=user_data.lessons_completed,
                    achievements_count=user_data.achievements_count,
                )

    return {
        "entries": entries,
        "current_user": current_user_entry,
        "last_updated": last_updated,
        "total_users": total_users,
    }
