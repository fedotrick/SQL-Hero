# Telegram Authentication Implementation

## Overview

This implementation provides Telegram WebApp authentication for the backend API. It validates Telegram init data using HMAC-SHA256 signature verification and creates or updates user records in the database.

## Features

- ✅ Validates Telegram WebApp init data with HMAC signature check
- ✅ Creates new users or syncs existing users on login
- ✅ Returns JWT access token for authenticated sessions
- ✅ Updates `last_active_date` on each login
- ✅ Normalizes username and first_name (trims whitespace, converts empty strings to NULL)
- ✅ Returns user profile payload with token
- ✅ Comprehensive test coverage

## Endpoint

### POST /auth/telegram

Authenticates a user via Telegram WebApp init data.

**Request Body:**
```json
{
  "init_data": "user=%7B%22id%22%3A12345678...&hash=abc123..."
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "telegram_id": 12345678,
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "language_code": "en",
    "is_active": true,
    "last_active_date": "2025-10-31T12:00:00Z",
    "created_at": "2025-10-31T12:00:00Z",
    "updated_at": "2025-10-31T12:00:00Z"
  }
}
```

**Error Responses:**

- `400 Bad Request`: Invalid init_data format or missing required fields
- `401 Unauthorized`: Invalid hash signature (HMAC check failed)

## Configuration

Add these environment variables:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=43200  # 30 days default
```

## Database Migration

A migration has been created to add the `last_active_date` field to the users table:

```bash
poetry run alembic upgrade head
```

## Files Created/Modified

### New Files:
- `app/core/security.py` - JWT token creation and validation
- `app/services/telegram_auth.py` - Telegram signature validation and user sync logic
- `app/schemas/auth.py` - Pydantic schemas for auth requests/responses
- `app/routers/auth.py` - Authentication endpoints
- `tests/test_auth_telegram.py` - Comprehensive test suite
- `alembic/versions/a8af3e20bfe3_add_last_active_date_to_users.py` - Database migration

### Modified Files:
- `app/core/config.py` - Added JWT configuration settings
- `app/models/database.py` - Added `last_active_date` field to User model
- `app/main.py` - Registered auth router
- `pyproject.toml` - Added PyJWT and aiosqlite dependencies

## Testing

Run the tests:

```bash
poetry run pytest tests/test_auth_telegram.py -v
```

The test suite covers:
- ✅ New user creation with valid Telegram data
- ✅ Existing user update and sync
- ✅ Invalid hash rejection
- ✅ Missing hash handling
- ✅ Invalid data format handling
- ✅ Missing user data handling
- ✅ Username/name normalization (trimming)
- ✅ Empty string normalization to NULL
- ✅ JWT token generation with user info
- ✅ Last active date updates

## Security

The implementation follows Telegram's authentication guidelines:

1. Validates the HMAC-SHA256 signature using the bot token
2. Checks that all data has been signed by Telegram
3. Rejects any tampered or invalid data
4. Uses secure JWT tokens for session management

## Usage Example

From a Telegram WebApp:

```javascript
// In your Telegram WebApp
const initData = window.Telegram.WebApp.initData;

// Send to backend
const response = await fetch('/auth/telegram', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    init_data: initData
  })
});

const data = await response.json();
// Store token: data.access_token
// User info: data.user
```
