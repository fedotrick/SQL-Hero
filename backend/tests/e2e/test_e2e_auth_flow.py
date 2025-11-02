"""E2E tests for authentication flow."""
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import User


class TestAuthenticationFlow:
    """Test complete authentication flow."""

    @pytest.mark.asyncio
    async def test_telegram_auth_creates_new_user(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that Telegram auth creates a new user."""
        # Simulate Telegram WebApp init data
        init_data = {
            "telegram_id": 987654321,
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "language_code": "en",
        }
        
        response = await client.post("/api/auth/telegram", json=init_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Verify user was created in database
        result = await db_session.execute(
            select(User).where(User.telegram_id == 987654321)
        )
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.username == "newuser"
        assert user.first_name == "New"
        assert user.last_active_date is not None

    @pytest.mark.asyncio
    async def test_telegram_auth_existing_user_updates_last_active(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that existing user's last_active_date is updated."""
        # Create existing user
        existing_user = User(
            telegram_id=111222333,
            username="existinguser",
            first_name="Existing",
            last_name="User",
            language_code="en",
        )
        db_session.add(existing_user)
        await db_session.commit()
        
        original_last_active = existing_user.last_active_date
        
        # Auth with existing user
        init_data = {
            "telegram_id": 111222333,
            "username": "existinguser",
            "first_name": "Existing",
            "last_name": "User",
            "language_code": "en",
        }
        
        response = await client.post("/api/auth/telegram", json=init_data)
        
        assert response.status_code == 200
        
        # Verify last_active_date was updated
        await db_session.refresh(existing_user)
        assert existing_user.last_active_date != original_last_active

    @pytest.mark.asyncio
    async def test_jwt_validation_requires_valid_token(self, client: AsyncClient):
        """Test that protected endpoints require valid JWT."""
        # Try to access protected endpoint without token
        response = await client.get("/api/user/profile")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_jwt_validation_rejects_invalid_token(self, client: AsyncClient):
        """Test that invalid JWT is rejected."""
        client.headers["Authorization"] = "Bearer invalid_token_here"
        response = await client.get("/api/user/profile")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_authenticated_access_with_valid_token(
        self, authenticated_client: AsyncClient
    ):
        """Test that valid JWT allows access to protected endpoints."""
        response = await authenticated_client.get("/api/user/profile")
        assert response.status_code == 200
        data = response.json()
        assert "telegram_id" in data
        assert "username" in data
        assert "xp" in data
        assert "level" in data


class TestAuthErrorHandling:
    """Test authentication error handling."""

    @pytest.mark.asyncio
    async def test_auth_with_invalid_telegram_data(self, client: AsyncClient):
        """Test auth with invalid Telegram data."""
        invalid_data = {
            "telegram_id": "not_a_number",  # Invalid type
            "username": "user",
        }
        
        response = await client.post("/api/auth/telegram", json=invalid_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_auth_with_missing_required_fields(self, client: AsyncClient):
        """Test auth with missing required fields."""
        incomplete_data = {
            "username": "user",
            # Missing telegram_id
        }
        
        response = await client.post("/api/auth/telegram", json=incomplete_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_expired_token_is_rejected(self, client: AsyncClient):
        """Test that expired JWT tokens are rejected."""
        from datetime import datetime, timedelta, timezone
        import jwt
        from app.core.config import settings
        
        # Create expired token
        payload = {
            "sub": "123456789",
            "telegram_id": 123456789,
            "username": "testuser",
            "exp": datetime.now(timezone.utc) - timedelta(days=1),  # Expired
        }
        expired_token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
        
        client.headers["Authorization"] = f"Bearer {expired_token}"
        response = await client.get("/api/user/profile")
        assert response.status_code == 401
