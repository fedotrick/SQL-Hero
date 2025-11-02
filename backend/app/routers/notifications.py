from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.database import (
    NotificationStatus,
    PendingNotification,
    User,
)
from app.schemas.notifications import (
    NotificationStats,
    PendingNotificationResponse,
    ReminderCampaignRequest,
    ReminderCampaignResponse,
)
from app.services.telegram_notifications import telegram_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


async def process_notifications_background(db_url: str) -> None:
    """Background task to process pending notifications."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    engine = create_async_engine(db_url)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await telegram_service.process_pending_notifications(session, limit=100)

    await engine.dispose()


@router.post(
    "/admin/reminder-campaign",
    response_model=ReminderCampaignResponse,
    summary="Trigger reminder campaign",
    description="Send reminder notifications to inactive users. Admin endpoint.",
)
async def trigger_reminder_campaign(
    campaign: ReminderCampaignRequest,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ReminderCampaignResponse:
    """
    Trigger a reminder campaign for inactive users.

    This endpoint allows admins to send reminder notifications to users who have been
    inactive for a specified number of days.

    Args:
        campaign: Campaign configuration including days_inactive, message, and notification_type
        background_tasks: FastAPI background tasks for async processing
        current_user: Current authenticated user (admin)
        db: Database session

    Returns:
        ReminderCampaignResponse: Information about queued notifications
    """
    cutoff_date = datetime.utcnow() - timedelta(days=campaign.days_inactive)

    inactive_users_query = select(User).where(
        (User.last_active_date < cutoff_date) | (User.last_active_date.is_(None)),
        User.is_active == True,  # noqa: E712
    )
    result = await db.execute(inactive_users_query)
    inactive_users = list(result.scalars().all())

    target_user_ids = []
    for user in inactive_users:
        await telegram_service.send_reminder_notification(
            db=db,
            user_id=user.id,
            message=campaign.message,
            reminder_type=campaign.notification_type,
        )
        target_user_ids.append(user.id)

    await db.commit()

    background_tasks.add_task(
        process_notifications_background,
        str(db.get_bind().url),
    )

    return ReminderCampaignResponse(
        queued_count=len(target_user_ids),
        target_users=target_user_ids,
    )


@router.get(
    "/admin/stats",
    response_model=NotificationStats,
    summary="Get notification statistics",
    description="Get statistics about notification delivery status. Admin endpoint.",
)
async def get_notification_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> NotificationStats:
    """
    Get notification statistics.

    Returns counts of notifications by status (pending, sent, failed).
    """
    total_query = select(func.count(PendingNotification.id))
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0

    pending_query = select(func.count(PendingNotification.id)).where(
        PendingNotification.status == NotificationStatus.PENDING
    )
    pending_result = await db.execute(pending_query)
    pending = pending_result.scalar() or 0

    sent_query = select(func.count(PendingNotification.id)).where(
        PendingNotification.status == NotificationStatus.SENT
    )
    sent_result = await db.execute(sent_query)
    sent = sent_result.scalar() or 0

    failed_query = select(func.count(PendingNotification.id)).where(
        PendingNotification.status == NotificationStatus.FAILED
    )
    failed_result = await db.execute(failed_query)
    failed = failed_result.scalar() or 0

    return NotificationStats(
        total=total,
        pending=pending,
        sent=sent,
        failed=failed,
    )


@router.post(
    "/admin/process",
    summary="Process pending notifications",
    description="Manually trigger processing of pending notifications. Admin endpoint.",
)
async def process_pending_notifications(
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Manually trigger processing of pending notifications.

    This endpoint starts a background task to process all pending notifications.
    """
    background_tasks.add_task(
        process_notifications_background,
        str(db.get_bind().url),
    )

    return {"status": "processing", "message": "Notification processing started"}


@router.get(
    "/admin/pending",
    response_model=list[PendingNotificationResponse],
    summary="List pending notifications",
    description="Get list of pending notifications. Admin endpoint.",
)
async def list_pending_notifications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 50,
) -> list[PendingNotificationResponse]:
    """
    Get list of pending notifications.

    Args:
        limit: Maximum number of notifications to return (default: 50)

    Returns:
        List of pending notifications
    """
    query = (
        select(PendingNotification)
        .where(PendingNotification.status == NotificationStatus.PENDING)
        .order_by(PendingNotification.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    notifications = result.scalars().all()

    return [
        PendingNotificationResponse(
            id=n.id,
            user_id=n.user_id,
            notification_type=n.notification_type.value,
            status=n.status.value,
            message=n.message,
            metadata=n.metadata,
            error_message=n.error_message,
            sent_at=n.sent_at,
            created_at=n.created_at,
            updated_at=n.updated_at,
        )
        for n in notifications
    ]
