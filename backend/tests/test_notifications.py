import random
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.database import (
    Achievement,
    AchievementType,
    Base,
    Lesson,
    Module,
    NotificationStatus,
    NotificationType,
    PendingNotification,
    ProgressStatus,
    User,
    UserProgress,
)
from app.services.achievements import evaluate_achievements
from app.services.telegram_notifications import TelegramNotificationService


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
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_module(db_session: AsyncSession):
    """Create a test module."""
    module = Module(
        title="Test Module",
        description="Test module description",
        order=1,
        is_published=True,
    )
    db_session.add(module)
    await db_session.commit()
    await db_session.refresh(module)
    return module


@pytest.fixture
async def test_lesson(db_session: AsyncSession, test_module: Module):
    """Create a test lesson."""
    lesson = Lesson(
        module_id=test_module.id,
        title="Test Lesson",
        content="Test content",
        order=1,
        estimated_duration=20,
        is_published=True,
    )
    db_session.add(lesson)
    await db_session.commit()
    await db_session.refresh(lesson)
    return lesson


@pytest.fixture
async def test_achievement(db_session: AsyncSession):
    """Create a test achievement."""
    achievement = Achievement(
        code="first_lesson",
        type=AchievementType.LESSON_COMPLETED,
        title="First Steps",
        description="Complete your first lesson",
        icon="🎓",
        points=10,
        criteria="Complete any lesson",
    )
    db_session.add(achievement)
    await db_session.commit()
    await db_session.refresh(achievement)
    return achievement


@pytest.fixture
def mock_telegram_service():
    """Create a mock telegram service."""
    return TelegramNotificationService(bot_token="test_token")


@pytest.mark.asyncio
async def test_queue_notification(db_session: AsyncSession, test_user: User):
    """Test queuing a notification."""
    service = TelegramNotificationService()

    notification = await service.queue_notification(
        db=db_session,
        user_id=test_user.id,
        notification_type=NotificationType.ACHIEVEMENT_UNLOCKED,
        message="Test notification",
        metadata={"test": "data"},
    )

    assert notification.id is not None
    assert notification.user_id == test_user.id
    assert notification.notification_type == NotificationType.ACHIEVEMENT_UNLOCKED
    assert notification.status == NotificationStatus.PENDING
    assert notification.message == "Test notification"
    assert notification.metadata == {"test": "data"}


@pytest.mark.asyncio
async def test_send_telegram_message_success(mock_telegram_service):
    """Test successful Telegram message sending."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True, "result": {"message_id": 123}}

    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance

        success, error = await mock_telegram_service._send_telegram_message(
            telegram_id=123456789,
            message="Test message",
        )

        assert success is True
        assert error is None
        mock_instance.post.assert_called_once()
        call_args = mock_instance.post.call_args
        assert "sendMessage" in call_args[0][0]
        assert call_args[1]["json"]["chat_id"] == 123456789
        assert call_args[1]["json"]["text"] == "Test message"
        assert call_args[1]["json"]["parse_mode"] == "HTML"


@pytest.mark.asyncio
async def test_send_telegram_message_api_error(mock_telegram_service):
    """Test Telegram API error handling."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": False, "description": "Bad Request: chat not found"}

    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance

        success, error = await mock_telegram_service._send_telegram_message(
            telegram_id=123456789,
            message="Test message",
        )

        assert success is False
        assert "Bad Request: chat not found" in error


@pytest.mark.asyncio
async def test_send_telegram_message_http_error(mock_telegram_service):
    """Test HTTP error handling."""
    mock_response = Mock()
    mock_response.status_code = 500

    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance

        success, error = await mock_telegram_service._send_telegram_message(
            telegram_id=123456789,
            message="Test message",
        )

        assert success is False
        assert "HTTP error: 500" in error


@pytest.mark.asyncio
async def test_send_notification_success(
    db_session: AsyncSession, test_user: User, mock_telegram_service
):
    """Test sending a notification successfully."""
    notification = await mock_telegram_service.queue_notification(
        db=db_session,
        user_id=test_user.id,
        notification_type=NotificationType.REMINDER,
        message="Test reminder",
    )
    await db_session.commit()

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True}

    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance

        success, error = await mock_telegram_service.send_notification(
            db=db_session, notification_id=notification.id
        )

        assert success is True
        assert error is None

    await db_session.refresh(notification)
    assert notification.status == NotificationStatus.SENT
    assert notification.sent_at is not None
    assert notification.error_message is None


@pytest.mark.asyncio
async def test_send_notification_failure(
    db_session: AsyncSession, test_user: User, mock_telegram_service
):
    """Test notification sending failure."""
    notification = await mock_telegram_service.queue_notification(
        db=db_session,
        user_id=test_user.id,
        notification_type=NotificationType.REMINDER,
        message="Test reminder",
    )
    await db_session.commit()

    mock_response = Mock()
    mock_response.status_code = 400

    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance

        success, error = await mock_telegram_service.send_notification(
            db=db_session, notification_id=notification.id
        )

        assert success is False
        assert error is not None

    await db_session.refresh(notification)
    assert notification.status == NotificationStatus.FAILED
    assert notification.error_message is not None


@pytest.mark.asyncio
async def test_achievement_unlock_triggers_notification(
    db_session: AsyncSession,
    test_user: User,
    test_module: Module,
    test_lesson: Lesson,
    test_achievement: Achievement,
):
    """Test that unlocking an achievement triggers a notification."""
    progress = UserProgress(
        user_id=test_user.id,
        lesson_id=test_lesson.id,
        status=ProgressStatus.COMPLETED,
        attempts=1,
        first_try=True,
        xp_earned=10,
        completed_at=datetime.utcnow(),
    )
    db_session.add(progress)
    await db_session.commit()

    with patch(
        "app.services.achievements.telegram_service.send_achievement_notification"
    ) as mock_notify:
        mock_notify.return_value = AsyncMock()

        newly_unlocked = await evaluate_achievements(db_session, test_user)

        assert len(newly_unlocked) == 1
        assert newly_unlocked[0].achievement_code == "first_lesson"

        mock_notify.assert_called_once()
        call_args = mock_notify.call_args
        assert call_args[1]["user_id"] == test_user.id
        assert call_args[1]["achievement_data"]["achievement_code"] == "first_lesson"


@pytest.mark.asyncio
async def test_format_achievement_message(mock_telegram_service):
    """Test achievement message formatting."""
    achievement_data = {
        "title": "First Steps",
        "description": "Complete your first lesson",
        "icon": "🎓",
        "points": 10,
    }

    message = mock_telegram_service._format_achievement_message(achievement_data)

    assert "🎓" in message
    assert "Achievement Unlocked!" in message
    assert "First Steps" in message
    assert "Complete your first lesson" in message
    assert "+10 points!" in message


@pytest.mark.asyncio
async def test_get_pending_notifications(
    db_session: AsyncSession, test_user: User, mock_telegram_service
):
    """Test retrieving pending notifications."""
    for i in range(5):
        await mock_telegram_service.queue_notification(
            db=db_session,
            user_id=test_user.id,
            notification_type=NotificationType.REMINDER,
            message=f"Test message {i}",
        )

    await db_session.commit()

    pending = await mock_telegram_service.get_pending_notifications(db_session, limit=10)

    assert len(pending) == 5
    assert all(n.status == NotificationStatus.PENDING for n in pending)


@pytest.mark.asyncio
async def test_process_pending_notifications(
    db_session: AsyncSession, test_user: User, mock_telegram_service
):
    """Test batch processing of pending notifications."""
    for i in range(3):
        await mock_telegram_service.queue_notification(
            db=db_session,
            user_id=test_user.id,
            notification_type=NotificationType.REMINDER,
            message=f"Test message {i}",
        )

    await db_session.commit()

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True}

    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance

        sent_count = await mock_telegram_service.process_pending_notifications(
            db_session, limit=10
        )

        assert sent_count == 3


@pytest.mark.asyncio
async def test_send_reminder_notification(
    db_session: AsyncSession, test_user: User, mock_telegram_service
):
    """Test sending a reminder notification."""
    notification = await mock_telegram_service.send_reminder_notification(
        db=db_session,
        user_id=test_user.id,
        message="Time to practice!",
        reminder_type="daily",
    )

    assert notification.notification_type == NotificationType.REMINDER
    assert notification.message == "Time to practice!"
    assert notification.metadata == {"reminder_type": "daily"}
    assert notification.status == NotificationStatus.PENDING


@pytest.mark.asyncio
async def test_notification_not_found(db_session: AsyncSession, mock_telegram_service):
    """Test sending notification with invalid ID."""
    success, error = await mock_telegram_service.send_notification(
        db=db_session, notification_id=99999
    )

    assert success is False
    assert "not found" in error.lower()


@pytest.mark.asyncio
async def test_notification_already_sent(
    db_session: AsyncSession, test_user: User, mock_telegram_service
):
    """Test attempting to send an already sent notification."""
    notification = await mock_telegram_service.queue_notification(
        db=db_session,
        user_id=test_user.id,
        notification_type=NotificationType.REMINDER,
        message="Test message",
    )
    notification.status = NotificationStatus.SENT
    await db_session.commit()

    success, error = await mock_telegram_service.send_notification(
        db=db_session, notification_id=notification.id
    )

    assert success is False
    assert "already processed" in error.lower()


@pytest.mark.asyncio
async def test_send_achievement_notification(
    db_session: AsyncSession, test_user: User, mock_telegram_service
):
    """Test sending an achievement notification."""
    achievement_data = {
        "achievement_id": 1,
        "achievement_code": "first_lesson",
        "title": "First Steps",
        "description": "Complete your first lesson",
        "icon": "🎓",
        "points": 10,
    }

    notification = await mock_telegram_service.send_achievement_notification(
        db=db_session,
        user_id=test_user.id,
        achievement_data=achievement_data,
    )

    assert notification.notification_type == NotificationType.ACHIEVEMENT_UNLOCKED
    assert notification.metadata == achievement_data
    assert notification.status == NotificationStatus.PENDING
    assert "🎓" in notification.message
    assert "First Steps" in notification.message


@pytest.mark.asyncio
async def test_telegram_message_payload_correctness(mock_telegram_service):
    """Test that Telegram API payload is correctly formatted."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True}

    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance

        await mock_telegram_service._send_telegram_message(
            telegram_id=987654321,
            message="<b>Test</b> message with HTML",
        )

        call_args = mock_instance.post.call_args
        payload = call_args[1]["json"]

        assert payload["chat_id"] == 987654321
        assert payload["text"] == "<b>Test</b> message with HTML"
        assert payload["parse_mode"] == "HTML"

        url = call_args[0][0]
        assert "https://api.telegram.org/bot" in url
        assert "/sendMessage" in url


@pytest.mark.asyncio
async def test_no_telegram_token(db_session: AsyncSession, test_user: User):
    """Test behavior when Telegram bot token is not configured."""
    service = TelegramNotificationService(bot_token="")

    notification = await service.queue_notification(
        db=db_session,
        user_id=test_user.id,
        notification_type=NotificationType.REMINDER,
        message="Test",
    )
    await db_session.commit()

    success, error = await service.send_notification(db=db_session, notification_id=notification.id)

    assert success is False
    assert "token not configured" in error.lower()

    await db_session.refresh(notification)
    assert notification.status == NotificationStatus.FAILED
