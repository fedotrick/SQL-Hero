import json
from datetime import datetime
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.database import (
    NotificationStatus,
    NotificationType,
    PendingNotification,
    User,
)


class TelegramNotificationService:
    def __init__(self, bot_token: str | None = None):
        self.bot_token = bot_token or settings.telegram_bot_token
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def queue_notification(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: NotificationType,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> PendingNotification:
        """Queue a notification for delivery."""
        notification = PendingNotification(
            user_id=user_id,
            notification_type=notification_type,
            message=message,
            metadata=metadata,
            status=NotificationStatus.PENDING,
        )
        db.add(notification)
        await db.flush()
        await db.refresh(notification)
        return notification

    async def send_notification(
        self, db: AsyncSession, notification_id: int
    ) -> tuple[bool, str | None]:
        """
        Send a pending notification via Telegram Bot API.

        Returns:
            tuple[bool, str | None]: (success, error_message)
        """
        notification_query = select(PendingNotification).where(
            PendingNotification.id == notification_id
        )
        result = await db.execute(notification_query)
        notification = result.scalar_one_or_none()

        if not notification:
            return False, "Notification not found"

        if notification.status != NotificationStatus.PENDING:
            return False, f"Notification already processed with status: {notification.status.value}"

        user_query = select(User).where(User.id == notification.user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            notification.status = NotificationStatus.FAILED
            notification.error_message = "User not found"
            notification.updated_at = datetime.utcnow()
            await db.commit()
            return False, "User not found"

        try:
            success, error = await self._send_telegram_message(
                telegram_id=user.telegram_id,
                message=notification.message,
            )

            if success:
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.utcnow()
                notification.error_message = None
            else:
                notification.status = NotificationStatus.FAILED
                notification.error_message = error

            notification.updated_at = datetime.utcnow()
            await db.commit()
            return success, error

        except Exception as e:
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(e)
            notification.updated_at = datetime.utcnow()
            await db.commit()
            return False, str(e)

    async def _send_telegram_message(
        self, telegram_id: int, message: str
    ) -> tuple[bool, str | None]:
        """
        Send a message via Telegram Bot API.

        Returns:
            tuple[bool, str | None]: (success, error_message)
        """
        if not self.bot_token:
            return False, "Telegram bot token not configured"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/sendMessage",
                    json={
                        "chat_id": telegram_id,
                        "text": message,
                        "parse_mode": "HTML",
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        return True, None
                    else:
                        error_msg = data.get("description", "Unknown error")
                        return False, f"Telegram API error: {error_msg}"
                else:
                    return False, f"HTTP error: {response.status_code}"

        except httpx.TimeoutException:
            return False, "Request timeout"
        except httpx.RequestError as e:
            return False, f"Request error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    async def send_achievement_notification(
        self, db: AsyncSession, user_id: int, achievement_data: dict[str, Any]
    ) -> PendingNotification:
        """Queue and optionally send an achievement notification."""
        message = self._format_achievement_message(achievement_data)

        notification = await self.queue_notification(
            db=db,
            user_id=user_id,
            notification_type=NotificationType.ACHIEVEMENT_UNLOCKED,
            message=message,
            metadata=achievement_data,
        )

        return notification

    async def send_reminder_notification(
        self, db: AsyncSession, user_id: int, message: str, reminder_type: str = "general"
    ) -> PendingNotification:
        """Queue a reminder notification."""
        notification = await self.queue_notification(
            db=db,
            user_id=user_id,
            notification_type=NotificationType.REMINDER,
            message=message,
            metadata={"reminder_type": reminder_type},
        )

        return notification

    def _format_achievement_message(self, achievement_data: dict[str, Any]) -> str:
        """Format an achievement notification message."""
        title = achievement_data.get("title", "Achievement Unlocked")
        description = achievement_data.get("description", "")
        points = achievement_data.get("points", 0)
        icon = achievement_data.get("icon", "🏆")

        message = f"{icon} <b>Achievement Unlocked!</b>\n\n"
        message += f"<b>{title}</b>\n"

        if description:
            message += f"{description}\n"

        message += f"\n+{points} points!"

        return message

    async def get_pending_notifications(
        self, db: AsyncSession, limit: int = 100
    ) -> list[PendingNotification]:
        """Get pending notifications to process."""
        query = (
            select(PendingNotification)
            .where(PendingNotification.status == NotificationStatus.PENDING)
            .order_by(PendingNotification.created_at)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def process_pending_notifications(self, db: AsyncSession, limit: int = 100) -> int:
        """
        Process pending notifications in batch.

        Returns:
            int: Number of successfully sent notifications
        """
        pending = await self.get_pending_notifications(db, limit)
        sent_count = 0

        for notification in pending:
            success, _ = await self.send_notification(db, notification.id)
            if success:
                sent_count += 1

        return sent_count


telegram_service = TelegramNotificationService()
