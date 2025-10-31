import hashlib
import hmac
import json
from datetime import UTC, datetime
from urllib.parse import urlencode

import httpx
import pytest
from httpx import ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import Base
from app.main import app
from app.models.database import User


@pytest.fixture
async def test_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_db(test_engine):
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def client(test_db):
    async def override_get_db():
        yield test_db

    from app.core.database import get_db

    app.dependency_overrides[get_db] = override_get_db

    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


def create_telegram_init_data(user_data: dict, bot_token: str) -> str:
    user_json = json.dumps(user_data, separators=(",", ":"))

    data = {
        "user": user_json,
        "auth_date": str(int(datetime.now(UTC).timestamp())),
        "query_id": "test_query_id",
    }

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(data.items()))

    secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()
    hash_value = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    data["hash"] = hash_value

    return urlencode(data)


async def test_telegram_auth_new_user(client: httpx.AsyncClient, test_db: AsyncSession):
    user_data = {
        "id": 12345678,
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
        "language_code": "en",
    }

    init_data = create_telegram_init_data(user_data, settings.telegram_bot_token)

    response = await client.post("/auth/telegram", json={"init_data": init_data})

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data

    user = data["user"]
    assert user["telegram_id"] == 12345678
    assert user["first_name"] == "John"
    assert user["last_name"] == "Doe"
    assert user["username"] == "johndoe"
    assert user["language_code"] == "en"
    assert user["is_active"] is True

    result = await test_db.execute(select(User).where(User.telegram_id == 12345678))
    db_user = result.scalar_one_or_none()
    assert db_user is not None
    assert db_user.username == "johndoe"
    assert db_user.first_name == "John"
    assert db_user.last_active_date is not None


async def test_telegram_auth_existing_user(client: httpx.AsyncClient, test_db: AsyncSession):
    existing_user = User(
        telegram_id=87654321,
        username="oldusername",
        first_name="Old",
        last_name="Name",
        language_code="ru",
        is_active=True,
        last_active_date=None,
    )
    test_db.add(existing_user)
    await test_db.commit()
    await test_db.refresh(existing_user)

    user_data = {
        "id": 87654321,
        "first_name": "Updated",
        "last_name": "User",
        "username": "newusername",
        "language_code": "en",
    }

    init_data = create_telegram_init_data(user_data, settings.telegram_bot_token)

    response = await client.post("/auth/telegram", json={"init_data": init_data})

    assert response.status_code == 200
    data = response.json()

    user = data["user"]
    assert user["telegram_id"] == 87654321
    assert user["first_name"] == "Updated"
    assert user["last_name"] == "User"
    assert user["username"] == "newusername"
    assert user["language_code"] == "en"

    result = await test_db.execute(select(User).where(User.telegram_id == 87654321))
    db_user = result.scalar_one_or_none()
    assert db_user is not None
    assert db_user.username == "newusername"
    assert db_user.first_name == "Updated"
    assert db_user.last_active_date is not None


async def test_telegram_auth_invalid_hash(client: httpx.AsyncClient):
    user_data = {
        "id": 12345678,
        "first_name": "John",
        "username": "johndoe",
    }

    init_data = create_telegram_init_data(user_data, "wrong_bot_token")

    response = await client.post("/auth/telegram", json={"init_data": init_data})

    assert response.status_code == 401
    assert "Invalid hash signature" in response.json()["detail"]


async def test_telegram_auth_missing_hash(client: httpx.AsyncClient):
    init_data = "user=%7B%22id%22%3A12345678%7D&auth_date=1234567890"

    response = await client.post("/auth/telegram", json={"init_data": init_data})

    assert response.status_code == 400
    assert "Missing hash in init_data" in response.json()["detail"]


async def test_telegram_auth_invalid_format(client: httpx.AsyncClient):
    init_data = "invalid_format_data"

    response = await client.post("/auth/telegram", json={"init_data": init_data})

    assert response.status_code == 400


async def test_telegram_auth_missing_user_data(client: httpx.AsyncClient):
    data = {
        "auth_date": str(int(datetime.now(UTC).timestamp())),
        "query_id": "test_query_id",
    }

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(data.items()))

    secret_key = hmac.new(
        "WebAppData".encode(), settings.telegram_bot_token.encode(), hashlib.sha256
    ).digest()
    hash_value = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    data["hash"] = hash_value
    init_data = urlencode(data)

    response = await client.post("/auth/telegram", json={"init_data": init_data})

    assert response.status_code == 400
    assert "Missing user data" in response.json()["detail"]


async def test_telegram_auth_normalize_username(client: httpx.AsyncClient, test_db: AsyncSession):
    user_data = {
        "id": 11111111,
        "first_name": "  Trimmed  ",
        "username": "  trimuser  ",
    }

    init_data = create_telegram_init_data(user_data, settings.telegram_bot_token)

    response = await client.post("/auth/telegram", json={"init_data": init_data})

    assert response.status_code == 200
    data = response.json()

    user = data["user"]
    assert user["first_name"] == "Trimmed"
    assert user["username"] == "trimuser"


async def test_telegram_auth_empty_strings_normalized(
    client: httpx.AsyncClient, test_db: AsyncSession
):
    user_data = {
        "id": 22222222,
        "first_name": "ValidName",
        "username": "   ",
        "last_name": "",
    }

    init_data = create_telegram_init_data(user_data, settings.telegram_bot_token)

    response = await client.post("/auth/telegram", json={"init_data": init_data})

    assert response.status_code == 200
    data = response.json()

    user = data["user"]
    assert user["first_name"] == "ValidName"
    assert user["username"] is None
    assert user["last_name"] is None


async def test_telegram_auth_token_contains_user_info(
    client: httpx.AsyncClient, test_db: AsyncSession
):
    user_data = {
        "id": 33333333,
        "first_name": "Token",
        "username": "tokentest",
    }

    init_data = create_telegram_init_data(user_data, settings.telegram_bot_token)

    response = await client.post("/auth/telegram", json={"init_data": init_data})

    assert response.status_code == 200
    data = response.json()

    access_token = data["access_token"]
    assert access_token is not None

    from app.core.security import decode_access_token

    payload = decode_access_token(access_token)
    assert "sub" in payload
    assert "telegram_id" in payload
    assert payload["telegram_id"] == 33333333


async def test_telegram_auth_updates_last_active_on_existing_user(
    client: httpx.AsyncClient, test_db: AsyncSession
):
    old_date = datetime(2020, 1, 1, 0, 0, 0)
    existing_user = User(
        telegram_id=99999999,
        username="activeuser",
        first_name="Active",
        is_active=True,
        last_active_date=old_date,
    )
    test_db.add(existing_user)
    await test_db.commit()
    await test_db.refresh(existing_user)

    user_data = {
        "id": 99999999,
        "first_name": "Active",
        "username": "activeuser",
    }

    init_data = create_telegram_init_data(user_data, settings.telegram_bot_token)

    response = await client.post("/auth/telegram", json={"init_data": init_data})

    assert response.status_code == 200

    result = await test_db.execute(select(User).where(User.telegram_id == 99999999))
    db_user = result.scalar_one_or_none()
    assert db_user is not None
    assert db_user.last_active_date is not None
    assert db_user.last_active_date > old_date
