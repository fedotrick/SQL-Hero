from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationBase(BaseModel):
    notification_type: str
    message: str
    notification_metadata: dict | None = None


class PendingNotificationCreate(NotificationBase):
    user_id: int


class PendingNotificationResponse(NotificationBase):
    id: int
    user_id: int
    status: str
    error_message: str | None = None
    sent_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationStats(BaseModel):
    total: int
    pending: int
    sent: int
    failed: int


class ReminderCampaignRequest(BaseModel):
    days_inactive: int = 7
    notification_type: str = "reminder"
    message: str


class ReminderCampaignResponse(BaseModel):
    queued_count: int
    target_users: list[int]
