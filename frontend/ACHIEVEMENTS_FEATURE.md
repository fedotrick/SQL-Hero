# Achievements Feature Implementation

## Overview
This document describes the implementation of the Achievements UI feature, which includes a comprehensive achievements system with earned/locked badges, progress indicators, unlock animations, and real-time updates.

## Features Implemented

### 1. Achievements List Screen
- **Location**: `src/pages/AchievementsPage.tsx`
- **Features**:
  - Display all achievements with earned vs locked status
  - Progress indicators for locked achievements showing current/target progress
  - Statistics overview (total earned, total points, completion percentage)
  - Visual distinction between earned and locked achievements (opacity)
  - Click on any achievement to view detailed information

### 2. Achievement Detail Modal
- **Location**: `src/components/achievements/AchievementDetailModal.tsx`
- **Features**:
  - Shows detailed information about an achievement
  - Displays achievement icon, title, description, and criteria
  - Shows unlock condition details
  - Displays points reward
  - For locked achievements: Shows progress bar and current/target values
  - For earned achievements: Shows unlock date and time
  - Smooth animation on open/close using framer-motion

### 3. Achievement Unlock Animation
- **Location**: `src/components/achievements/AchievementUnlockAnimation.tsx`
- **Features**:
  - Celebratory animation when a new achievement is unlocked
  - Sparkles and ripple effects for visual appeal
  - Shows achievement details with points earned
  - Auto-dismisses after 2.5 seconds
  - Uses framer-motion for smooth animations

### 4. Real-time Achievement Updates
- **Location**: `src/hooks/useAchievements.ts`
- **Features**:
  - Polls achievements API every 10 seconds (configurable)
  - Detects newly unlocked achievements
  - Triggers unlock animation when new achievements are earned
  - Maintains state of previously earned achievements to detect changes
  - Callback support for custom handling of new achievements

### 5. Achievements API Service
- **Location**: `src/services/achievements.ts`
- **Features**:
  - Fetches achievements from backend API
  - Handles authentication with Bearer token
  - Comprehensive error handling
  - Type-safe responses using TypeScript

### 6. Data Formatting Utilities
- **Location**: `src/utils/achievementFormatters.ts`
- **Features**:
  - Format dates in Russian locale
  - Format progress percentages and ratios
  - Calculate completion statistics
  - Sort and filter achievements by status
  - Get achievement status text
  - Calculate total points earned

## Type Definitions
- **Location**: `src/types/achievements.ts`
- **Types**:
  - `Achievement` - Complete achievement with all fields
  - `AchievementProgress` - Progress tracking (current, target, percentage)
  - `AchievementsListResponse` - API response structure
  - `AchievementUnlocked` - Notification format for newly unlocked achievements

## Tests
Comprehensive test coverage for all functionality:

### Service Tests
- **File**: `src/services/achievements.test.ts`
- Tests API calls, error handling, and data formatting

### Component Tests
- **File**: `src/pages/AchievementsPage.test.tsx`
- Tests rendering, loading states, error states, progress display, and statistics

### Utility Tests
- **File**: `src/utils/achievementFormatters.test.ts`
- Tests all data formatting functions with various input scenarios

## API Integration

### Endpoint
```
GET /achievements
```

### Authentication
```
Authorization: Bearer <token>
```

### Response Format
```typescript
{
  achievements: [
    {
      id: number,
      code: string,
      type: string,
      title: string,
      description: string | null,
      icon: string | null,
      points: number,
      criteria: string | null,
      created_at: string,
      is_earned: boolean,
      earned_at: string | null,
      progress: {
        current: number,
        target: number,
        percentage: number
      } | null
    }
  ],
  total_earned: number,
  total_points: number
}
```

## Polling Mechanism
The achievements are refreshed every 10 seconds using React Query's `refetchInterval` option. When the API detects a newly earned achievement (by comparing achievement IDs), it triggers the unlock animation.

## User Experience

1. **Initial Load**: Shows loading screen while fetching achievements
2. **Main View**: Displays statistics at top, followed by list of all achievements
3. **Achievement Interaction**: Click any achievement to view details
4. **Progress Tracking**: Locked achievements show progress bars
5. **Real-time Updates**: New achievements automatically trigger celebration animation
6. **Error Handling**: Graceful error display with user-friendly messages

## Styling
- Uses Telegram theme variables for consistent look
- Responsive design for mobile and desktop
- Smooth animations using framer-motion
- Icons from lucide-react library

## Configuration
- **Polling Interval**: Configurable in `useAchievements` hook (default: 10 seconds)
- **Animation Duration**: Unlock animation shows for 2.5 seconds
- **API Base URL**: Configurable via `VITE_API_URL` environment variable

## Future Enhancements
Potential improvements for future iterations:
- WebSocket support for instant updates instead of polling
- Achievement categories/filters
- Share achievement on social media
- Achievement sound effects
- Achievement notification history
