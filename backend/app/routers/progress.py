from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.database import User
from app.schemas.progress import (
    LessonAttemptRequest,
    LessonAttemptResponse,
    UserProgressSummary,
)
from app.services.progress import get_user_progress_summary, submit_lesson_attempt

router = APIRouter(prefix="/progress", tags=["progress"])


@router.post(
    "/lessons/{lesson_id}/attempt",
    response_model=LessonAttemptResponse,
    summary="Submit lesson attempt",
    description=(
        "Submit a lesson attempt with SQL query. "
        "Updates user progress, XP, level, streak, and tracks first_try flag. "
        "Uses transactional handling to prevent race conditions."
    ),
)
async def attempt_lesson(
    lesson_id: int,
    attempt: LessonAttemptRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LessonAttemptResponse:
    """
    Submit a lesson attempt.

    The endpoint handles:
    - Tracking attempts and first_try flag
    - Awarding XP based on first_try bonus
    - Updating user level based on XP
    - Maintaining daily activity streaks
    - Recording query count
    - Transitioning lesson status (NOT_STARTED -> IN_PROGRESS -> COMPLETED)

    XP Formula:
    - Base XP: 50 points per lesson
    - First try bonus: +25 points (awarded only if first attempt succeeds)

    Level Formula:
    - Level = floor(XP / 100) + 1
    - Each level requires 100 XP

    Streak Logic:
    - Increments if user was active yesterday
    - Resets to 1 if streak was broken (missed a day)
    - Tracks longest streak achieved
    """
    try:
        result = await submit_lesson_attempt(
            db=db,
            user=current_user,
            lesson_id=lesson_id,
            user_query=attempt.user_query,
            success=attempt.success,
        )

        return LessonAttemptResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit attempt: {str(e)}",
        )


@router.get(
    "/summary",
    response_model=UserProgressSummary,
    summary="Get user progress summary",
    description=(
        "Get comprehensive progress summary for the authenticated user. "
        "Includes XP, level, streaks, completion stats, and more for dashboard display."
    ),
)
async def get_progress_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserProgressSummary:
    """
    Get user progress summary for dashboard.

    Returns:
    - Current XP and level
    - Progress within current level (percentage)
    - XP needed to reach next level
    - Current and longest streak
    - Total queries submitted
    - Lessons and modules completion stats
    - Achievement count
    - Last activity date
    """
    summary = await get_user_progress_summary(db, current_user)
    return UserProgressSummary(**summary)
