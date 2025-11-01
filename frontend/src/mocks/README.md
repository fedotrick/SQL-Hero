# Mock Telegram WebApp

This directory contains mock implementations of the Telegram WebApp API for testing and development.

## Usage

### In Browser Console (Development)

```javascript
// Enable mock Telegram WebApp
window.enableMockTelegram();

// Reload page to see the app authenticate with mock data
location.reload();

// Disable mock
window.disableMockTelegram();
```

### In Test Files

```typescript
import {
  installMockTelegramWebApp,
  uninstallMockTelegramWebApp,
  createMockTelegramWebApp
} from "./telegramWebApp";

// Install mock before tests
beforeEach(() => {
  installMockTelegramWebApp();
});

// Clean up after tests
afterEach(() => {
  uninstallMockTelegramWebApp();
});

// Test example
test("should authenticate with mock data", async () => {
  // Mock is installed, app will use it
  render(<App />);

  // Wait for authentication
  await waitFor(() => {
    expect(screen.getByText(/welcome/i)).toBeInTheDocument();
  });
});
```

### Custom Mock Data

```typescript
import { installMockTelegramWebApp } from "./telegramWebApp";

// Install with custom user data
installMockTelegramWebApp({
  initDataUnsafe: {
    user: {
      id: 999,
      first_name: "Custom",
      last_name: "User",
      username: "customuser",
    },
    auth_date: Date.now(),
    hash: "custom_hash",
  },
});
```

## Mock Features

The mock WebApp provides:

- ✅ Full WebApp API interface
- ✅ Realistic initData string
- ✅ User data
- ✅ Haptic feedback (logs to console)
- ✅ Theme parameters
- ✅ All WebApp methods
- ✅ Console logging for debugging

## Backend Mock

To test the full flow including backend, you need to:

1. Either run the backend with mock mode enabled
2. Or mock the fetch API to return expected responses

Example fetch mock:

```typescript
global.fetch = jest.fn((url) => {
  if (url.includes("/auth/telegram")) {
    return Promise.resolve({
      ok: true,
      json: async () => ({
        access_token: "mock_token",
        token_type: "bearer",
        user: {
          id: 1,
          telegram_id: 123456789,
          username: "testuser",
          first_name: "Test",
          last_name: "User",
          language_code: "en",
          is_active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      }),
    });
  }
  return Promise.reject(new Error("Not found"));
});
```

## Notes

- The mock simulates a Telegram user with ID `123456789`
- All haptic feedback calls are logged to console
- The mock is only available in development mode
- Mock data won't work with real backend (hash validation will fail)
