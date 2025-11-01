from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.database import User
from app.schemas.leaderboard import LeaderboardResponse, RefreshLeaderboardResponse
from app.services.leaderboard import get_leaderboard, refresh_leaderboard_cache

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get(
    "",
    response_model=LeaderboardResponse,
    summary="Get leaderboard",
    description=(
        "Get the top N users from the leaderboard, ordered by XP. "
        "If the current user is not in the top N, their rank is included separately. "
        "Results are cached for performance."
    ),
)
async def get_leaderboard_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(default=100, ge=1, le=1000, description="Number of top users to return"),
) -> LeaderboardResponse:
    """
    Get leaderboard with top N users and current user's rank.

    Args:
        current_user: Authenticated user
        db: Database session
        limit: Number of top users to return (1-1000, default 100)

    Returns:
        LeaderboardResponse with:
        - entries: List of top N users
        - current_user: Current user's entry if not in top N
        - last_updated: Timestamp of last cache refresh
        - total_users: Total number of users in leaderboard
    """
    result = await get_leaderboard(db, limit=limit, user_id=current_user.id)
    return LeaderboardResponse(**result)


@router.post(
    "/refresh",
    response_model=RefreshLeaderboardResponse,
    summary="Refresh leaderboard cache",
    description=(
        "Refresh the leaderboard cache from users' XP data. "
        "This operation is concurrency-safe and can be triggered by cron jobs or manually."
    ),
)
async def refresh_leaderboard_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RefreshLeaderboardResponse:
    """
    Refresh the leaderboard cache.

    This endpoint recalculates all user ranks based on current XP data.
    It's safe to call concurrently as it uses database transactions.

    Returns:
        RefreshLeaderboardResponse with:
        - success: Whether the refresh succeeded
        - message: Status message
        - entries_updated: Number of cache entries updated
        - timestamp: When the refresh completed
    """
    entries_updated = await refresh_leaderboard_cache(db)

    return RefreshLeaderboardResponse(
        success=True,
        message="Leaderboard cache refreshed successfully",
        entries_updated=entries_updated,
        timestamp=datetime.utcnow(),
    )
