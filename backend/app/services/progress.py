from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import (
    ActivityLog,
    ActivityType,
    Lesson,
    Module,
    ProgressStatus,
    User,
    UserAchievement,
    UserProgress,
)


def calculate_xp_for_lesson(lesson_id: int, first_try: bool) -> int:
    """
    Calculate XP earned for completing a lesson.
    
    Formula:
    - Base XP: 50 points per lesson
    - First try bonus: +25 points (50% bonus)
    """
    base_xp = 50
    first_try_bonus = 25 if first_try else 0
    return base_xp + first_try_bonus


def calculate_level_from_xp(xp: int) -> int:
    """
    Calculate user level based on total XP.
    
    Formula: level = floor(xp / 100) + 1
    Each level requires 100 XP.
    """
    return (xp // 100) + 1


def calculate_xp_for_level(level: int) -> tuple[int, int]:
    """
    Calculate XP range for a given level.
    
    Returns:
        tuple[int, int]: (current_level_xp, next_level_xp)
    """
    current_level_xp = (level - 1) * 100
    next_level_xp = level * 100
    return current_level_xp, next_level_xp


async def update_user_streak(db: AsyncSession, user: User) -> tuple[int, int]:
    """
    Update user's streak based on last activity date.
    
    Rules:
    - If last_active_date is today: no change
    - If last_active_date is yesterday: increment streak
    - If last_active_date is older or None: reset to 1
    
    Returns:
        tuple[int, int]: (current_streak, longest_streak)
    """
    today = date.today()
    
    if user.last_active_date:
        last_active = user.last_active_date.date()
        
        if last_active == today:
            # Already logged activity today, no change
            return user.current_streak, user.longest_streak
        elif last_active == today - timedelta(days=1):
            # Yesterday: increment streak
            user.current_streak += 1
        else:
            # Streak broken: reset to 1
            user.current_streak = 1
    else:
        # First activity
        user.current_streak = 1
    
    # Update longest streak if current exceeds it
    if user.current_streak > user.longest_streak:
        user.longest_streak = user.current_streak
    
    # Update last active date
    user.last_active_date = datetime.utcnow()
    
    return user.current_streak, user.longest_streak


async def submit_lesson_attempt(
    db: AsyncSession,
    user: User,
    lesson_id: int,
    user_query: str,
    success: bool,
) -> dict:
    """
    Submit a lesson attempt and update user progress transactionally.
    
    This function handles:
    - Creating/updating UserProgress record
    - Tracking attempts and first_try flag
    - Awarding XP and updating level
    - Updating streak
    - Logging activity
    
    Args:
        db: Database session
        user: Current user
        lesson_id: ID of the lesson being attempted
        user_query: SQL query submitted by user
        success: Whether the query succeeded
        
    Returns:
        dict: Response data with updated stats
    """
    # Verify lesson exists
    lesson_query = select(Lesson).where(Lesson.id == lesson_id)
    lesson_result = await db.execute(lesson_query)
    lesson = lesson_result.scalar_one_or_none()
    
    if not lesson:
        raise ValueError("Lesson not found")
    
    # Get or create user progress
    progress_query = select(UserProgress).where(
        UserProgress.user_id == user.id,
        UserProgress.lesson_id == lesson_id,
    )
    progress_result = await db.execute(progress_query)
    progress = progress_result.scalar_one_or_none()
    
    is_new = progress is None
    level_before = user.level
    
    if is_new:
        progress = UserProgress(
            user_id=user.id,
            lesson_id=lesson_id,
            status=ProgressStatus.IN_PROGRESS,
            attempts=0,
            started_at=datetime.utcnow(),
        )
        db.add(progress)
    
    # Increment attempts
    progress.attempts += 1
    
    # Track first_try flag (set on first attempt only)
    if progress.attempts == 1:
        progress.first_try = success
    
    # Increment total queries for user
    user.total_queries += 1
    
    xp_earned = 0
    progress_status_changed = False
    
    if success:
        # Only award XP if this is the first successful completion
        if progress.status != ProgressStatus.COMPLETED:
            # Calculate XP based on first_try flag
            xp_earned = calculate_xp_for_lesson(lesson_id, progress.first_try or False)
            progress.xp_earned = xp_earned
            
            # Update user XP and level
            user.xp += xp_earned
            user.level = calculate_level_from_xp(user.xp)
            
            # Mark lesson as completed
            progress.status = ProgressStatus.COMPLETED
            progress.completed_at = datetime.utcnow()
            progress_status_changed = True
            
            # Log completion activity
            activity_log = ActivityLog(
                user_id=user.id,
                activity_type=ActivityType.LESSON_COMPLETED,
                entity_id=lesson_id,
                entity_type="lesson",
                details=f"Completed in {progress.attempts} attempts. XP earned: {xp_earned}",
            )
            db.add(activity_log)
        
        # Update streak
        current_streak, longest_streak = await update_user_streak(db, user)
    else:
        # Failed attempt - log it
        activity_log = ActivityLog(
            user_id=user.id,
            activity_type=ActivityType.CHALLENGE_ATTEMPTED,
            entity_id=lesson_id,
            entity_type="lesson",
            details=f"Attempt {progress.attempts} failed",
        )
        db.add(activity_log)
    
    # Commit transaction
    await db.commit()
    await db.refresh(user)
    await db.refresh(progress)
    
    level_up = user.level > level_before
    
    # Calculate level progress
    current_level_xp, next_level_xp = calculate_xp_for_level(user.level)
    
    # Generate response message
    if success:
        if progress_status_changed:
            message = f"Congratulations! You've completed the lesson and earned {xp_earned} XP!"
        else:
            message = "Correct! You've already completed this lesson."
    else:
        message = f"Not quite right. Try again! (Attempt {progress.attempts})"
    
    return {
        "success": success,
        "xp_earned": xp_earned,
        "total_xp": user.xp,
        "level": user.level,
        "level_up": level_up,
        "current_streak": user.current_streak,
        "longest_streak": user.longest_streak,
        "attempts": progress.attempts,
        "first_try": progress.first_try or False,
        "progress_status": progress.status.value,
        "message": message,
    }


async def get_user_progress_summary(db: AsyncSession, user: User) -> dict:
    """
    Get comprehensive progress summary for user dashboard.
    
    Returns:
        dict: Summary with XP, level, streaks, completion stats, etc.
    """
    # Count completed lessons
    completed_lessons_query = select(func.count(UserProgress.id)).where(
        UserProgress.user_id == user.id,
        UserProgress.status == ProgressStatus.COMPLETED,
    )
    completed_lessons_result = await db.execute(completed_lessons_query)
    lessons_completed = completed_lessons_result.scalar_one()
    
    # Count total published lessons
    total_lessons_query = select(func.count(Lesson.id)).where(Lesson.is_published == True)  # noqa: E712
    total_lessons_result = await db.execute(total_lessons_query)
    total_lessons = total_lessons_result.scalar_one()
    
    # Count modules with all lessons completed
    # Get all published modules
    modules_query = (
        select(Module)
        .where(Module.is_published == True)  # noqa: E712
        .order_by(Module.order)
    )
    modules_result = await db.execute(modules_query)
    modules = list(modules_result.scalars().all())
    
    # Get all lessons for modules
    lessons_query = select(Lesson).where(Lesson.is_published == True)  # noqa: E712
    lessons_result = await db.execute(lessons_query)
    all_lessons = list(lessons_result.scalars().all())
    
    # Get user progress
    progress_query = select(UserProgress).where(UserProgress.user_id == user.id)
    progress_result = await db.execute(progress_query)
    progress_map = {p.lesson_id: p for p in progress_result.scalars().all()}
    
    # Count completed modules
    modules_completed = 0
    for module in modules:
        module_lessons = [l for l in all_lessons if l.module_id == module.id]
        if module_lessons:
            completed_in_module = sum(
                1
                for lesson in module_lessons
                if progress_map.get(lesson.id)
                and progress_map[lesson.id].status == ProgressStatus.COMPLETED
            )
            if completed_in_module == len(module_lessons):
                modules_completed += 1
    
    total_modules = len(modules)
    
    # Count achievements
    achievements_query = select(func.count(UserAchievement.id)).where(
        UserAchievement.user_id == user.id
    )
    achievements_result = await db.execute(achievements_query)
    achievements_count = achievements_result.scalar_one()
    
    # Calculate level progress
    current_level_xp, next_level_xp = calculate_xp_for_level(user.level)
    xp_to_next_level = next_level_xp - user.xp
    
    # Calculate progress percentage within current level
    xp_in_level = user.xp - current_level_xp
    xp_needed_for_level = next_level_xp - current_level_xp
    progress_percentage = (xp_in_level / xp_needed_for_level * 100) if xp_needed_for_level > 0 else 0
    
    return {
        "user_id": user.id,
        "username": user.username,
        "xp": user.xp,
        "level": user.level,
        "xp_to_next_level": xp_to_next_level,
        "current_level_xp": current_level_xp,
        "next_level_xp": next_level_xp,
        "progress_percentage": round(progress_percentage, 2),
        "current_streak": user.current_streak,
        "longest_streak": user.longest_streak,
        "total_queries": user.total_queries,
        "lessons_completed": lessons_completed,
        "total_lessons": total_lessons,
        "modules_completed": modules_completed,
        "total_modules": total_modules,
        "achievements_count": achievements_count,
        "last_active_date": user.last_active_date,
    }
