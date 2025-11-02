import random
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import create_access_token
from app.main import app
from app.models.database import Base, NotificationStatus, NotificationType, PendingNotification, User


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def engine():
    """Create test database engine."""
    test_engine = create_async_engine(settings.database_url, echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
async def db_session(engine):
    """Create a new database session for each test."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = User(
        telegram_id=random.randint(100000000, 999999999),
        username="testuser",
        first_name="Test",
        last_name="User",
        xp=0,
        level=1,
        current_streak=0,
        longest_streak=0,
        total_queries=0,
        last_active_date=datetime.utcnow() - timedelta(days=10),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def inactive_users(db_session: AsyncSession):
    """Create multiple inactive test users."""
    users = []
    for i in range(3):
        user = User(
            telegram_id=random.randint(100000000, 999999999),
            username=f"inactiveuser{i}",
            first_name=f"Inactive{i}",
            last_name="User",
            xp=0,
            level=1,
            current_streak=0,
            longest_streak=0,
            total_queries=0,
            last_active_date=datetime.utcnow() - timedelta(days=10),
        )
        db_session.add(user)
        users.append(user)

    await db_session.commit()
    for user in users:
        await db_session.refresh(user)
    return users


@pytest.fixture
def auth_headers(test_user: User):
    """Create authentication headers."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_trigger_reminder_campaign_endpoint(
    test_user: User, inactive_users: list[User], auth_headers: dict, db_session: AsyncSession
):
    """Test the reminder campaign endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with patch(
            "app.routers.notifications.telegram_service.send_reminder_notification"
        ) as mock_notify:
            mock_notify.return_value = AsyncMock(
                id=1,
                notification_type=NotificationType.REMINDER,
                status=NotificationStatus.PENDING,
            )

            response = await client.post(
                "/notifications/admin/reminder-campaign",
                headers=auth_headers,
                json={
                    "days_inactive": 7,
                    "notification_type": "reminder",
                    "message": "Come back and learn!",
                },
            )

            assert response.status_code == 200
            data = response.json()

            assert "queued_count" in data
            assert "target_users" in data
            assert data["queued_count"] >= 0
            assert isinstance(data["target_users"], list)


@pytest.mark.asyncio
async def test_get_notification_stats_endpoint(
    test_user: User, auth_headers: dict, db_session: AsyncSession
):
    """Test the notification stats endpoint."""
    notification = PendingNotification(
        user_id=test_user.id,
        notification_type=NotificationType.REMINDER,
        status=NotificationStatus.PENDING,
        message="Test notification",
    )
    db_session.add(notification)
    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/notifications/admin/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "total" in data
        assert "pending" in data
        assert "sent" in data
        assert "failed" in data
        assert data["total"] >= 1
        assert data["pending"] >= 1


@pytest.mark.asyncio
async def test_process_pending_notifications_endpoint(test_user: User, auth_headers: dict):
    """Test the manual process endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/notifications/admin/process", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "processing"
        assert "message" in data


@pytest.mark.asyncio
async def test_list_pending_notifications_endpoint(
    test_user: User, auth_headers: dict, db_session: AsyncSession
):
    """Test the list pending notifications endpoint."""
    for i in range(3):
        notification = PendingNotification(
            user_id=test_user.id,
            notification_type=NotificationType.REMINDER,
            status=NotificationStatus.PENDING,
            message=f"Test notification {i}",
            metadata={"test": i},
        )
        db_session.add(notification)

    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/notifications/admin/pending?limit=10", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) >= 3

        for notification in data:
            assert "id" in notification
            assert "user_id" in notification
            assert "notification_type" in notification
            assert "status" in notification
            assert "message" in notification
            assert notification["status"] == "pending"


@pytest.mark.asyncio
async def test_reminder_campaign_with_custom_message(
    test_user: User, inactive_users: list[User], auth_headers: dict, db_session: AsyncSession
):
    """Test reminder campaign with custom message."""
    custom_message = "We miss you! Come back and continue learning SQL."

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with patch(
            "app.routers.notifications.telegram_service.send_reminder_notification"
        ) as mock_notify:
            mock_notify.return_value = AsyncMock()

            response = await client.post(
                "/notifications/admin/reminder-campaign",
                headers=auth_headers,
                json={
                    "days_inactive": 5,
                    "notification_type": "reminder",
                    "message": custom_message,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "queued_count" in data


@pytest.mark.asyncio
async def test_notification_stats_with_mixed_statuses(
    test_user: User, auth_headers: dict, db_session: AsyncSession
):
    """Test notification stats with different statuses."""
    notifications = [
        PendingNotification(
            user_id=test_user.id,
            notification_type=NotificationType.REMINDER,
            status=NotificationStatus.PENDING,
            message="Pending 1",
        ),
        PendingNotification(
            user_id=test_user.id,
            notification_type=NotificationType.REMINDER,
            status=NotificationStatus.SENT,
            message="Sent 1",
            sent_at=datetime.utcnow(),
        ),
        PendingNotification(
            user_id=test_user.id,
            notification_type=NotificationType.REMINDER,
            status=NotificationStatus.FAILED,
            message="Failed 1",
            error_message="Test error",
        ),
    ]

    for notification in notifications:
        db_session.add(notification)

    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/notifications/admin/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["total"] >= 3
        assert data["pending"] >= 1
        assert data["sent"] >= 1
        assert data["failed"] >= 1


@pytest.mark.asyncio
async def test_unauthenticated_access_denied():
    """Test that unauthenticated requests are denied."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/notifications/admin/reminder-campaign",
            json={
                "days_inactive": 7,
                "notification_type": "reminder",
                "message": "Test",
            },
        )

        assert response.status_code == 403


@pytest.mark.asyncio
async def test_pending_notifications_limit(
    test_user: User, auth_headers: dict, db_session: AsyncSession
):
    """Test that limit parameter works correctly."""
    for i in range(10):
        notification = PendingNotification(
            user_id=test_user.id,
            notification_type=NotificationType.REMINDER,
            status=NotificationStatus.PENDING,
            message=f"Test notification {i}",
        )
        db_session.add(notification)

    await db_session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/notifications/admin/pending?limit=5", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert len(data) <= 5


@pytest.mark.asyncio
async def test_reminder_campaign_no_inactive_users(test_user: User, auth_headers: dict):
    """Test reminder campaign when no users match criteria."""
    test_user.last_active_date = datetime.utcnow()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with patch(
            "app.routers.notifications.telegram_service.send_reminder_notification"
        ) as mock_notify:
            mock_notify.return_value = AsyncMock()

            response = await client.post(
                "/notifications/admin/reminder-campaign",
                headers=auth_headers,
                json={
                    "days_inactive": 30,
                    "notification_type": "reminder",
                    "message": "Test",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["queued_count"] >= 0
