import hashlib
import hmac
from datetime import UTC, datetime
from urllib.parse import parse_qsl

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.database import User


def validate_telegram_init_data(init_data: str) -> dict[str, str]:
    try:
        parsed_data = dict(parse_qsl(init_data))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid init_data format: {str(e)}",
        ) from e

    received_hash = parsed_data.pop("hash", None)
    if not received_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing hash in init_data"
        )

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed_data.items()))

    secret_key = hmac.new(
        b"WebAppData", settings.telegram_bot_token.encode(), hashlib.sha256
    ).digest()

    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if calculated_hash != received_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid hash signature"
        )

    return parsed_data


def normalize_string(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized if normalized else None


async def get_or_create_user(db: AsyncSession, telegram_data: dict[str, str]) -> User:
    if "user" not in telegram_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing user data")

    try:
        import json

        user_data = json.loads(telegram_data["user"])
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid user data format: {str(e)}",
        ) from e

    telegram_id = user_data.get("id")
    if not telegram_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing telegram user ID"
        )

    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    username = normalize_string(user_data.get("username"))
    first_name = normalize_string(user_data.get("first_name"))
    last_name = normalize_string(user_data.get("last_name"))
    language_code = user_data.get("language_code")

    if user:
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.language_code = language_code
        user.last_active_date = datetime.now(UTC)
        user.updated_at = datetime.now(UTC)
    else:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            is_active=True,
            last_active_date=datetime.now(UTC),
        )
        db.add(user)

    await db.flush()
    await db.refresh(user)

    return user
