# Telegram WebApp Integration

This document describes the Telegram WebApp integration implementation in the frontend application.

## Overview

The application is fully integrated with Telegram WebApp SDK, providing automatic authentication, haptic feedback, and graceful degradation when opened outside Telegram.

## Features

### 1. Automatic Authentication

- **Bootstrap on Load**: App automatically authenticates when launched in Telegram
- **Token Storage**: JWT tokens are stored in localStorage for session persistence
- **User Profile**: User information is fetched and cached
- **Loading States**: Smooth loading UI during authentication

### 2. Error Handling

- **Not in Telegram**: Shows a warning screen when app is opened outside Telegram
- **Auth Errors**: Displays error messages with retry option
- **Network Errors**: Handles network failures gracefully

### 3. Haptic Feedback Service

The app includes a comprehensive haptic feedback service with the following capabilities:

#### Impact Styles

- `light()` - Light impact feedback
- `medium()` - Medium impact feedback
- `heavy()` - Heavy impact feedback

#### Notifications

- `success()` - Success notification feedback
- `error()` - Error notification feedback
- `warning()` - Warning notification feedback

#### Other

- `selectionChanged()` - Selection change feedback
- `isAvailable()` - Check if haptics are available

The service automatically falls back gracefully when haptics are not available (outside Telegram).

## Architecture

### Service Layer

#### `telegramService` (`src/services/telegram.ts`)

Core Telegram WebApp integration service:

- `isAvailable()` - Check if running in Telegram
- `getInitData()` - Get raw init data string
- `getInitDataUnsafe()` - Get parsed init data
- `ready()` - Signal app is ready
- `expand()` - Expand app to full viewport
- `showAlert()` - Show Telegram alert
- `showConfirm()` - Show confirmation dialog
- Helper methods for platform, version, theme info

#### `authService` (`src/services/auth.ts`)

Authentication service:

- `authenticateWithTelegram(initData)` - Call backend auth endpoint
- `makeAuthenticatedRequest()` - Make API calls with token

#### `telegramHaptics` (`src/services/telegramHaptics.ts`)

Haptic feedback service with stub implementation that logs when unavailable.

### State Management

#### `useAuthStore` (`src/store/authStore.ts`)

Zustand store managing authentication state:

- `status`: `idle | loading | authenticated | error | not-in-telegram`
- `token`: JWT access token
- `user`: User profile data
- `error`: Error message if any

Actions:

- `setLoading()` - Set loading state
- `setAuthenticated(token, user)` - Set authenticated state
- `setError(error)` - Set error state
- `setNotInTelegram()` - Set not-in-telegram state
- `logout()` - Clear auth state
- `initialize()` - Initialize from stored data

### Components

#### `<TelegramAuthProvider>` (`src/components/TelegramAuthProvider.tsx`)

Main authentication provider that:

1. Checks if running in Telegram
2. Fetches initData from Telegram WebApp
3. Calls backend auth endpoint
4. Stores token and user data
5. Handles all error states
6. Shows appropriate UI for each state

#### `<LoadingScreen>` (`src/components/LoadingScreen.tsx`)

Loading state UI with spinner.

#### `<ErrorScreen>` (`src/components/ErrorScreen.tsx`)

Error state UI with retry button.

#### `<NotInTelegram>` (`src/components/NotInTelegram.tsx`)

Warning screen when opened outside Telegram.

### Storage

#### `storage` (`src/utils/storage.ts`)

LocalStorage wrapper for:

- Token persistence
- User profile caching
- Safe error handling

### Types

#### `src/types/telegram.ts`

Complete TypeScript definitions for:

- `TelegramWebApp` - Full WebApp API interface
- `TelegramUser` - User object
- `TelegramWebAppInitData` - Init data structure
- `TelegramHapticFeedback` - Haptic feedback API

## Testing

### Mock WebApp API

The app includes a comprehensive mock implementation for testing outside Telegram:

#### `src/mocks/telegramWebApp.ts`

- `createMockTelegramWebApp()` - Create mock WebApp instance
- `installMockTelegramWebApp()` - Install mock globally
- `uninstallMockTelegramWebApp()` - Remove mock

### Development Tools

When running in development mode, the following tools are available in browser console:

```javascript
// Enable mock Telegram WebApp for testing
window.enableMockTelegram();

// Disable mock
window.disableMockTelegram();
```

This allows you to test the full authentication flow without opening the app in Telegram.

## Usage Examples

### Using Authentication State

```typescript
import { useAuthStore } from "./store/authStore";

function MyComponent() {
  const { user, token, status } = useAuthStore();

  if (status === "loading") {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <p>Welcome, {user?.first_name}!</p>
      <p>Token: {token}</p>
    </div>
  );
}
```

### Using Haptic Feedback

```typescript
import { telegramHaptics } from "./services/telegramHaptics";

function MyButton() {
  const handleClick = () => {
    telegramHaptics.light(); // Trigger light haptic
    // ... do something
  };

  const handleSuccess = () => {
    telegramHaptics.success(); // Trigger success notification
    // ... show success message
  };

  return (
    <>
      <button onClick={handleClick}>Click Me</button>
      <button onClick={handleSuccess}>Success</button>
    </>
  );
}
```

### Using Telegram Service

```typescript
import { telegramService } from "./services/telegram";

function MyComponent() {
  const showInfo = async () => {
    await telegramService.showAlert("Hello from Telegram!");
  };

  const confirmAction = async () => {
    const confirmed = await telegramService.showConfirm(
      "Are you sure?"
    );
    if (confirmed) {
      // ... do something
    }
  };

  const theme = telegramService.getColorScheme();
  const platform = telegramService.getPlatform();

  return (
    <div>
      <p>Platform: {platform}</p>
      <p>Theme: {theme}</p>
      <button onClick={showInfo}>Show Alert</button>
      <button onClick={confirmAction}>Confirm</button>
    </div>
  );
}
```

### Making Authenticated API Calls

```typescript
import { authService } from "./services/auth";
import { useAuthStore } from "./store/authStore";

function MyComponent() {
  const { token } = useAuthStore();

  const fetchData = async () => {
    if (!token) return;

    const data = await authService.makeAuthenticatedRequest(
      "/api/my-endpoint",
      token
    );
    console.log(data);
  };

  return <button onClick={fetchData}>Fetch Data</button>;
}
```

## Authentication Flow

1. **App Loads** → `TelegramAuthProvider` mounts
2. **Check Telegram** → `telegramService.isAvailable()`
   - If NO → Show `<NotInTelegram>` screen
   - If YES → Continue
3. **Get Init Data** → `telegramService.getInitData()`
   - If empty → Show `<NotInTelegram>` screen
   - If present → Continue
4. **Authenticate** → `authService.authenticateWithTelegram(initData)`
   - Shows `<LoadingScreen>` during request
   - On success → Store token & user, show app
   - On error → Show `<ErrorScreen>` with retry
5. **App Ready** → User sees authenticated app

## Environment Variables

```env
VITE_API_URL=http://localhost:8000
```

Backend API URL for authentication endpoint.

## Backend Integration

The frontend expects the backend to provide:

### `POST /auth/telegram`

**Request:**

```json
{
  "init_data": "user=%7B%22id%22%3A12345...&auth_date=1234567890&hash=abc123..."
}
```

**Response:**

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
    "last_active_date": "2025-10-31T17:30:00Z",
    "created_at": "2025-10-31T17:30:00Z",
    "updated_at": "2025-10-31T17:30:00Z"
  }
}
```

**Error Response (401):**

```json
{
  "detail": "Invalid hash signature"
}
```

## Security

- **HMAC Validation**: Backend validates init data using bot token
- **Token Storage**: Tokens stored in localStorage (consider httpOnly cookies for production)
- **Auto Logout**: Implement token expiration handling
- **HTTPS Only**: Use HTTPS in production

## Production Considerations

1. **Token Refresh**: Implement token refresh mechanism
2. **Error Tracking**: Add error tracking service (Sentry, etc.)
3. **Analytics**: Track authentication events
4. **Performance**: Monitor auth timing
5. **Offline Support**: Handle offline scenarios
6. **Token Security**: Consider using httpOnly cookies instead of localStorage

## Troubleshooting

### App shows "Not Available" screen in Telegram

1. Check if Telegram SDK is loaded (check browser console)
2. Verify `window.Telegram.WebApp` exists
3. Check if `initData` is present

### Authentication fails

1. Check backend is running and accessible
2. Verify `VITE_API_URL` is correct
3. Check browser console for error messages
4. Try using mock mode: `window.enableMockTelegram()`

### Haptics don't work

1. Verify running in Telegram mobile app
2. Check device supports haptics
3. Check haptics are enabled in device settings
4. Note: Haptics don't work in Telegram Desktop

## Files Created

```
frontend/src/
├── types/
│   └── telegram.ts                    # TypeScript definitions
├── services/
│   ├── telegram.ts                    # Core Telegram service
│   ├── telegramHaptics.ts            # Haptics service (stub)
│   └── auth.ts                        # Authentication service
├── store/
│   └── authStore.ts                   # Auth state management
├── components/
│   ├── TelegramAuthProvider.tsx      # Main auth provider
│   ├── LoadingScreen.tsx             # Loading UI
│   ├── ErrorScreen.tsx               # Error UI
│   └── NotInTelegram.tsx             # Warning UI
├── mocks/
│   └── telegramWebApp.ts             # Mock WebApp for testing
└── utils/
    ├── storage.ts                     # Token storage utilities
    └── devTools.ts                    # Development helpers
```

## Resources

- [Telegram WebApp Documentation](https://core.telegram.org/bots/webapps)
- [Backend Auth Implementation](../../TELEGRAM_AUTH_IMPLEMENTATION.md)
