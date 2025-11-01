from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.database import User
from app.schemas.achievements import AchievementsListResponse
from app.services.achievements import get_user_achievements

router = APIRouter(prefix="/achievements", tags=["achievements"])


@router.get(
    "",
    response_model=AchievementsListResponse,
    summary="Get user achievements",
    description=(
        "Get all achievements with their status (earned/locked) and progress hints. "
        "Earned achievements include the date they were unlocked. "
        "Locked achievements include progress indicators showing how close the user is to unlocking them."
    ),
)
async def list_achievements(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AchievementsListResponse:
    """
    Get all achievements for the current user.

    Returns:
    - List of all achievements with their status
    - For earned achievements: includes earned_at timestamp
    - For locked achievements: includes progress indicators
    - Total count of earned achievements
    - Total points earned from achievements

    Progress hints help users understand:
    - Current progress (e.g., 5/10 lessons completed)
    - Target value needed to unlock
    - Percentage completion
    """
    result = await get_user_achievements(db, current_user)
    return AchievementsListResponse(**result)
