from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import (
    Achievement,
    ActivityLog,
    ActivityType,
    Lesson,
    Module,
    ProgressStatus,
    User,
    UserAchievement,
    UserProgress,
)
from app.schemas.achievements import (
    AchievementProgress,
    AchievementUnlockedNotification,
    AchievementWithStatus,
)
from app.services.telegram_notifications import telegram_service


async def evaluate_achievements(
    db: AsyncSession, user: User
) -> list[AchievementUnlockedNotification]:
    """
    Evaluate all achievement conditions for a user and unlock any newly earned achievements.

    This function checks all achievement conditions and persists any newly unlocked
    achievements in the user_achievements table. It also creates activity log entries
    that can be used for notifications.

    Returns:
        list[AchievementUnlockedNotification]: List of newly unlocked achievements
    """
    newly_unlocked: list[AchievementUnlockedNotification] = []

    # Get all existing user achievements
    existing_query = select(UserAchievement.achievement_id).where(
        UserAchievement.user_id == user.id
    )
    existing_result = await db.execute(existing_query)
    existing_achievement_ids = set(existing_result.scalars().all())

    # Get all achievements
    achievements_query = select(Achievement).order_by(Achievement.id)
    achievements_result = await db.execute(achievements_query)
    all_achievements = list(achievements_result.scalars().all())

    # Get user progress data
    progress_query = select(UserProgress).where(
        UserProgress.user_id == user.id,
        UserProgress.status == ProgressStatus.COMPLETED,
    )
    progress_result = await db.execute(progress_query)
    completed_progress = list(progress_result.scalars().all())

    # Count completed lessons
    lessons_completed = len(completed_progress)

    # Get modules with all lessons completed
    modules_query = select(Module).where(Module.is_published == True)  # noqa: E712
    modules_result = await db.execute(modules_query)
    all_modules = list(modules_result.scalars().all())

    lessons_query = select(Lesson).where(Lesson.is_published == True)  # noqa: E712
    lessons_result = await db.execute(lessons_query)
    all_lessons = list(lessons_result.scalars().all())

    progress_map = {p.lesson_id: p for p in completed_progress}

    completed_module_ids = []
    for module in all_modules:
        module_lessons = [lesson for lesson in all_lessons if lesson.module_id == module.id]
        if module_lessons:
            completed_in_module = sum(1 for lesson in module_lessons if lesson.id in progress_map)
            if completed_in_module == len(module_lessons):
                completed_module_ids.append(module.id)

    modules_completed = len(completed_module_ids)
    total_modules = len(all_modules)

    # Check each achievement
    for achievement in all_achievements:
        # Skip if already earned
        if achievement.id in existing_achievement_ids:
            continue

        earned = False

        # Evaluate based on achievement type and code
        if achievement.code == "first_lesson":
            earned = lessons_completed >= 1

        elif achievement.code == "ten_lessons":
            earned = lessons_completed >= 10

        elif achievement.code == "module_1_complete":
            earned = 1 in completed_module_ids

        elif achievement.code == "all_modules":
            earned = modules_completed == total_modules and total_modules > 0

        elif achievement.code == "streak_7":
            earned = user.current_streak >= 7

        elif achievement.code == "streak_30":
            earned = user.current_streak >= 30

        elif achievement.code == "challenge_master":
            # Count as total queries for now
            earned = user.total_queries >= 50

        elif achievement.code == "perfect_score":
            # Check if any lesson was completed on first try
            earned = any(p.first_try for p in completed_progress)

        elif achievement.code == "speed_runner":
            # Check if any lesson was completed faster than estimated
            for progress in completed_progress:
                if progress.started_at and progress.completed_at:
                    duration = (progress.completed_at - progress.started_at).total_seconds() / 60
                    lesson = next(
                        (lesson for lesson in all_lessons if lesson.id == progress.lesson_id), None
                    )
                    if (
                        lesson
                        and lesson.estimated_duration
                        and duration < lesson.estimated_duration
                    ):
                        earned = True
                        break

        elif achievement.code == "night_owl":
            # Check if any lesson was completed between 00:00 and 06:00
            for progress in completed_progress:
                if progress.completed_at:
                    hour = progress.completed_at.hour
                    if 0 <= hour < 6:
                        earned = True
                        break

        # If earned, persist the achievement
        if earned:
            user_achievement = UserAchievement(
                user_id=user.id,
                achievement_id=achievement.id,
                earned_at=datetime.utcnow(),
            )
            db.add(user_achievement)

            # Log the achievement unlock
            activity_log = ActivityLog(
                user_id=user.id,
                activity_type=ActivityType.ACHIEVEMENT_EARNED,
                entity_id=achievement.id,
                entity_type="achievement",
                details=f"Unlocked achievement: {achievement.title}",
            )
            db.add(activity_log)

            # Add to newly unlocked list
            achievement_notification = AchievementUnlockedNotification(
                achievement_id=achievement.id,
                achievement_code=achievement.code,
                title=achievement.title,
                description=achievement.description,
                icon=achievement.icon,
                points=achievement.points,
            )
            newly_unlocked.append(achievement_notification)

            # Queue notification for delivery
            await telegram_service.send_achievement_notification(
                db=db,
                user_id=user.id,
                achievement_data={
                    "achievement_id": achievement.id,
                    "achievement_code": achievement.code,
                    "title": achievement.title,
                    "description": achievement.description,
                    "icon": achievement.icon,
                    "points": achievement.points,
                },
            )

    # Commit all changes
    if newly_unlocked:
        await db.commit()

    return newly_unlocked


async def get_user_achievements(db: AsyncSession, user: User) -> dict[str, Any]:
    """
    Get all achievements with their status and progress for a user.

    Returns:
        dict: Dictionary with achievements list, total earned, and total points
    """
    # Get all achievements
    achievements_query = select(Achievement).order_by(Achievement.type, Achievement.points)
    achievements_result = await db.execute(achievements_query)
    all_achievements = list(achievements_result.scalars().all())

    # Get user's earned achievements
    user_achievements_query = select(UserAchievement).where(UserAchievement.user_id == user.id)
    user_achievements_result = await db.execute(user_achievements_query)
    user_achievements_list = list(user_achievements_result.scalars().all())
    user_achievements_map = {ua.achievement_id: ua for ua in user_achievements_list}

    # Get user progress data for calculating progress hints
    progress_query = select(UserProgress).where(
        UserProgress.user_id == user.id,
        UserProgress.status == ProgressStatus.COMPLETED,
    )
    progress_result = await db.execute(progress_query)
    completed_progress = list(progress_result.scalars().all())

    lessons_completed = len(completed_progress)

    # Get modules completion data
    modules_query = select(Module).where(Module.is_published == True)  # noqa: E712
    modules_result = await db.execute(modules_query)
    all_modules = list(modules_result.scalars().all())

    lessons_query = select(Lesson).where(Lesson.is_published == True)  # noqa: E712
    lessons_result = await db.execute(lessons_query)
    all_lessons = list(lessons_result.scalars().all())

    progress_map = {p.lesson_id: p for p in completed_progress}

    completed_module_ids = []
    for module in all_modules:
        module_lessons = [lesson for lesson in all_lessons if lesson.module_id == module.id]
        if module_lessons:
            completed_in_module = sum(1 for lesson in module_lessons if lesson.id in progress_map)
            if completed_in_module == len(module_lessons):
                completed_module_ids.append(module.id)

    modules_completed = len(completed_module_ids)
    total_modules = len(all_modules)

    # Build achievements with status and progress
    achievements_with_status = []
    total_points = 0

    for achievement in all_achievements:
        user_achievement = user_achievements_map.get(achievement.id)
        is_earned = user_achievement is not None

        if is_earned:
            total_points += achievement.points

        # Calculate progress for locked achievements
        progress: AchievementProgress | None = None
        if not is_earned:
            if achievement.code == "first_lesson":
                progress = AchievementProgress(
                    current=min(lessons_completed, 1),
                    target=1,
                    percentage=min(lessons_completed * 100, 100),
                )
            elif achievement.code == "ten_lessons":
                progress = AchievementProgress(
                    current=min(lessons_completed, 10),
                    target=10,
                    percentage=min(lessons_completed / 10 * 100, 100),
                )
            elif achievement.code == "module_1_complete":
                module_1_lessons = [lesson for lesson in all_lessons if lesson.module_id == 1]
                completed_in_module_1 = sum(
                    1 for lesson in module_1_lessons if lesson.id in progress_map
                )
                total_in_module_1 = len(module_1_lessons)
                progress = AchievementProgress(
                    current=completed_in_module_1,
                    target=total_in_module_1,
                    percentage=(completed_in_module_1 / total_in_module_1 * 100)
                    if total_in_module_1 > 0
                    else 0,
                )
            elif achievement.code == "all_modules":
                progress = AchievementProgress(
                    current=modules_completed,
                    target=total_modules,
                    percentage=(modules_completed / total_modules * 100)
                    if total_modules > 0
                    else 0,
                )
            elif achievement.code == "streak_7":
                progress = AchievementProgress(
                    current=min(user.current_streak, 7),
                    target=7,
                    percentage=min(user.current_streak / 7 * 100, 100),
                )
            elif achievement.code == "streak_30":
                progress = AchievementProgress(
                    current=min(user.current_streak, 30),
                    target=30,
                    percentage=min(user.current_streak / 30 * 100, 100),
                )
            elif achievement.code == "challenge_master":
                progress = AchievementProgress(
                    current=min(user.total_queries, 50),
                    target=50,
                    percentage=min(user.total_queries / 50 * 100, 100),
                )
            elif achievement.code == "perfect_score":
                first_try_count = sum(1 for p in completed_progress if p.first_try)
                progress = AchievementProgress(
                    current=min(first_try_count, 1),
                    target=1,
                    percentage=min(first_try_count * 100, 100),
                )

        achievements_with_status.append(
            AchievementWithStatus(
                id=achievement.id,
                code=achievement.code,
                type=achievement.type.value,
                title=achievement.title,
                description=achievement.description,
                icon=achievement.icon,
                points=achievement.points,
                criteria=achievement.criteria,
                created_at=achievement.created_at,
                is_earned=is_earned,
                earned_at=user_achievement.earned_at if user_achievement else None,
                progress=progress,
            )
        )

    return {
        "achievements": achievements_with_status,
        "total_earned": len(user_achievements_list),
        "total_points": total_points,
    }
