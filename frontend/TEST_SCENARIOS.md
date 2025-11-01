# Test Scenarios for Telegram WebApp Integration

## Scenario 1: Opening in Telegram (Real Environment)

**Prerequisites:**
- Backend server running at configured API URL
- Bot created with valid token
- Mini app configured in BotFather

**Steps:**
1. Open mini app through Telegram bot
2. Observe loading screen appears briefly
3. App authenticates automatically
4. Homepage shows user information (name, username, Telegram ID)
5. Haptic feedback works when tapping demo buttons
6. Theme matches Telegram's current theme

**Expected Result:**
✅ Automatic authentication  
✅ User info displayed  
✅ Haptics functional  
✅ No errors in console  

## Scenario 2: Opening Outside Telegram

**Steps:**
1. Open app URL directly in browser (not through Telegram)
2. Observe warning screen

**Expected Result:**
✅ Shows "Not Available" warning screen  
✅ Explains app must be opened in Telegram  
✅ Provides instructions  
✅ No crash or error  

## Scenario 3: Using Mock Mode (Development)

**Prerequisites:**
- Backend server running (or can be mocked)

**Steps:**
1. Open app in browser
2. See "Not in Telegram" warning
3. Open browser console
4. Type: `window.enableMockTelegram()`
5. Reload page
6. Observe authentication with mock data

**Expected Result:**
✅ Mock WebApp installed  
✅ App authenticates with mock user  
✅ Mock user data displayed  
✅ Haptic calls logged to console  

## Scenario 4: Authentication Error Handling

**Prerequisites:**
- Backend returns 401 error

**Steps:**
1. Configure backend to reject auth
2. Open app in Telegram
3. Observe error screen
4. Click "Try Again" button

**Expected Result:**
✅ Shows error screen with message  
✅ Retry button functional  
✅ Can attempt authentication again  

## Scenario 5: Network Error Handling

**Prerequisites:**
- Backend is unreachable

**Steps:**
1. Stop backend server
2. Open app in Telegram (or use mock mode)
3. Observe error screen

**Expected Result:**
✅ Shows network error message  
✅ Retry button available  
✅ No app crash  

## Scenario 6: Session Persistence

**Steps:**
1. Authenticate successfully in Telegram
2. Refresh the page
3. Observe app loads without re-authentication

**Expected Result:**
✅ App loads immediately  
✅ User still authenticated  
✅ No second auth call  
✅ Token persisted in localStorage  

## Scenario 7: Haptic Feedback Demo

**Prerequisites:**
- Open in Telegram mobile app
- Device supports haptics

**Steps:**
1. Navigate to Haptic Feedback Demo section on homepage
2. Tap "Light" button
3. Tap "Medium" button
4. Tap "Heavy" button
5. Tap "Success" button
6. Tap "Error" button
7. Tap "Warning" button

**Expected Result:**
✅ Each button triggers appropriate haptic feedback  
✅ Different intensities felt for impact styles  
✅ Different patterns for notifications  

## Scenario 8: Telegram WebApp Info Display

**Steps:**
1. Open app in Telegram
2. Scroll to "Telegram WebApp Info" section
3. Verify displayed information

**Expected Result:**
✅ Platform shown (ios, android, web, etc.)  
✅ Version shown  
✅ Color scheme shown (light/dark)  
✅ Available: Yes  
✅ Haptics Available: Yes (on mobile)  

## Automated Testing Checklist

### Unit Tests (Future)
- [ ] `telegramService.isAvailable()` returns correct value
- [ ] `telegramService.getInitData()` returns initData string
- [ ] `authService.authenticateWithTelegram()` calls correct endpoint
- [ ] `authStore` state transitions work correctly
- [ ] `storage` utils handle errors gracefully
- [ ] `telegramHaptics` logs when unavailable

### Integration Tests (Future)
- [ ] Mock WebApp can be installed/uninstalled
- [ ] Auth flow works end-to-end with mock
- [ ] Error states render correctly
- [ ] Loading states render correctly

### E2E Tests (Future)
- [ ] Full authentication flow
- [ ] Navigation after auth
- [ ] Token persistence across reloads
- [ ] Logout and re-auth

## Console Commands for Testing

```javascript
// Check if Telegram WebApp is available
window.Telegram?.WebApp

// Enable mock for testing
window.enableMockTelegram()

// Disable mock
window.disableMockTelegram()

// Check auth state
// (in React DevTools or add window.authStore = useAuthStore in dev)

// Clear stored token
localStorage.clear()

// View stored token
localStorage.getItem('telegram_auth_token')

// View stored user
JSON.parse(localStorage.getItem('telegram_user'))
```

## Manual QA Checklist

### Visual
- [ ] Loading spinner centered and animated
- [ ] Error screen styled correctly
- [ ] Warning screen styled correctly
- [ ] Homepage displays user info in card
- [ ] Haptic buttons styled with appropriate colors
- [ ] All text readable in light theme
- [ ] All text readable in dark theme

### Functional
- [ ] Authentication works in Telegram
- [ ] Warning shows outside Telegram
- [ ] Mock mode works for development
- [ ] Error screen shows on auth failure
- [ ] Retry button works on error screen
- [ ] Haptics trigger on button press
- [ ] Token persists across reloads
- [ ] App respects Telegram theme

### Error Cases
- [ ] Backend unreachable - shows error
- [ ] Backend returns 401 - shows error
- [ ] Backend returns 500 - shows error
- [ ] Invalid initData - shows error
- [ ] Empty initData - shows warning
- [ ] No Telegram WebApp - shows warning

### Performance
- [ ] Loading screen shows immediately
- [ ] Auth completes in < 2 seconds (with good network)
- [ ] No unnecessary re-renders
- [ ] No memory leaks

## Known Limitations

1. **Haptics unavailable in Telegram Desktop** - This is a Telegram limitation
2. **Mock mode requires manual backend** - Must either run backend or mock fetch
3. **Token in localStorage** - Consider httpOnly cookies for production
4. **No token refresh** - Implement refresh token mechanism for production
5. **No offline support** - App requires network for initial auth

## Browser Compatibility

Tested/Should work in:
- ✅ Chrome/Edge (Chromium)
- ✅ Safari (iOS)
- ✅ Firefox
- ✅ Telegram WebView (iOS)
- ✅ Telegram WebView (Android)

## Device Testing

Should be tested on:
- [ ] iPhone (Safari, Telegram)
- [ ] Android (Chrome, Telegram)
- [ ] Desktop (Chrome, Firefox, Safari)
- [ ] Telegram Desktop
