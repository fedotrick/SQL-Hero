# UI Shell Components Documentation

This document describes the UI shell components implementation for the Telegram Mini App.

## Overview

The UI shell components system provides a comprehensive set of reusable primitives aligned with Telegram design tokens. All components are responsive, support dark mode, and feature smooth animations using Framer Motion.

## Components Implemented

### 1. Button Component
**Location:** `src/components/ui/Button.tsx`

A versatile button component with multiple variants and states.

**Features:**
- 5 variants: primary, secondary, outline, ghost, destructive
- 3 sizes: sm, md, lg
- Icon support (left/right)
- Loading state with spinner
- Tap animation
- Full width option
- Disabled state

**Example:**
```tsx
<Button variant="primary" size="md" leftIcon={<Plus />}>
  Add Item
</Button>
```

### 2. Card Component
**Location:** `src/components/ui/Card.tsx`

Container component for grouping related content with multiple sub-components.

**Features:**
- 3 variants: default, elevated, outlined
- 4 padding options: none, sm, md, lg
- Interactive mode with hover/tap effects
- Sub-components: CardHeader, CardTitle, CardContent

**Example:**
```tsx
<Card variant="elevated" interactive>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content</CardContent>
</Card>
```

### 3. Badge Component
**Location:** `src/components/ui/Badge.tsx`

Small labels for displaying status, metadata, or categories.

**Features:**
- 6 variants: default, success, warning, error, info, outline
- 3 sizes: sm, md, lg
- Optional dot indicator
- Fade-in animation

**Example:**
```tsx
<Badge variant="success" dot>Active</Badge>
```

### 4. ProgressBar Component
**Location:** `src/components/ui/ProgressBar.tsx`

Linear and circular progress indicators.

**Features:**
- Linear and circular variants
- 4 color variants: default, success, warning, error
- 3 sizes for linear bars
- Customizable circular size and stroke
- Optional labels
- Smooth animations

**Example:**
```tsx
<ProgressBar value={65} showLabel label="Progress" />
<CircularProgress value={75} size={80} />
```

### 5. BottomNavigation Component
**Location:** `src/components/ui/BottomNavigation.tsx`

Fixed bottom navigation bar with three main sections.

**Features:**
- Fixed positioning at bottom
- 3 navigation items:
  - Курс (Course) - with BookOpen icon
  - Достижения (Achievements) - with Trophy icon
  - Профиль (Profile) - with User icon
- Active state indicator with slide animation
- Icon scale animation on active
- Safe area support for notched devices
- Integrated with React Router

**Example:**
```tsx
<BottomNavigation />
```

## Pages Implemented

### 1. HomePage (Курс)
**Location:** `src/pages/HomePage.tsx`

Main course page displaying user progress and quick actions.

**Features:**
- User profile card
- Progress tracking with progress bars
- Quick action buttons
- Haptic feedback demo
- Link to component showcase
- Telegram WebApp info

### 2. AchievementsPage (Достижения)
**Location:** `src/pages/AchievementsPage.tsx`

Displays user achievements and statistics.

**Features:**
- Statistics cards (unlocked/total, points, completion %)
- Achievement list with icons
- Locked/unlocked states
- Progress indicators for incomplete achievements

### 3. ProfilePage (Профиль)
**Location:** `src/pages/ProfilePage.tsx`

User profile and statistics page.

**Features:**
- User avatar and info
- Level and XP progress
- Statistics grid (lessons, achievements, hours, progress)
- Settings menu
- App information

### 4. ComponentShowcase
**Location:** `src/pages/ComponentShowcase.tsx`

Comprehensive showcase of all UI components.

**Features:**
- Live examples of all components
- All variants and sizes demonstrated
- Interactive controls (e.g., progress slider)
- Component combination examples
- Design system information

## Design Tokens

**Location:** `src/utils/designTokens.ts`

Centralized design tokens including:
- Colors (using Telegram CSS variables)
- Spacing (xs to 2xl)
- Border radius (sm to full)
- Font sizes (xs to 3xl)
- Font weights
- Shadows
- Transitions

## Styling Approach

### Telegram Design Tokens Integration
All components use Telegram design tokens through CSS variables:
```css
--tg-theme-bg-color
--tg-theme-text-color
--tg-theme-button-color
--tg-theme-button-text-color
--tg-theme-secondary-bg-color
... and more
```

### Tailwind CSS
Components use Tailwind utility classes with custom Telegram color classes:
```tsx
className="bg-telegram-button text-telegram-button-text"
```

### Dark Mode Support
Automatic dark mode support through Telegram theme switching. Colors adapt based on user's Telegram theme.

## Animations

All animations use Framer Motion for smooth, performant effects:

1. **Button:** Scale on tap (0.95)
2. **Card:** Scale on hover (1.02) and tap (0.98) when interactive
3. **Badge:** Fade in with scale animation
4. **ProgressBar:** Smooth fill animation (0.5s ease-out)
5. **CircularProgress:** Circular stroke animation
6. **BottomNavigation:** 
   - Active indicator slide with spring animation
   - Icon scale (1.1) when active

## Responsive Design

### Mobile-First Approach
- Components optimized for Telegram's 480px max width
- Touch-friendly sizes (min 44px tap targets)
- Flexible layouts
- Safe area support for notched devices

### Breakpoints
Using Tailwind's default breakpoints plus custom:
- `telegram: { max: "480px" }` - Telegram-specific breakpoint

## Accessibility

All components follow accessibility best practices:
- Semantic HTML elements
- Proper ARIA labels
- Keyboard navigation
- Focus indicators
- Screen reader friendly
- Color contrast compliance

## Usage in Application

### Importing Components
```tsx
import { Button, Card, Badge, ProgressBar, BottomNavigation } from "@/components/ui";
```

### Layout Integration
BottomNavigation is integrated into BaseLayout:
```tsx
<BaseLayout>
  <main>{children}</main>
  <BottomNavigation />
</BaseLayout>
```

### Routing
All pages are configured in `src/routes/index.tsx`:
- `/` - HomePage (Курс)
- `/achievements` - AchievementsPage (Достижения)
- `/profile` - ProfilePage (Профиль)
- `/showcase` - ComponentShowcase

## Testing

Components can be tested:
1. Visit `/showcase` to see all components in action
2. Test responsiveness by resizing browser
3. Toggle dark mode using header button
4. Test haptic feedback in Telegram app
5. Navigate between pages using bottom navigation

## Dependencies Added

```json
{
  "framer-motion": "^12.23.24",
  "lucide-react": "^0.552.0"
}
```

## File Structure

```
src/
├── components/
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── ProgressBar.tsx
│   │   ├── BottomNavigation.tsx
│   │   ├── index.ts
│   │   └── README.md
│   └── layout/
│       └── BaseLayout.tsx (updated)
├── pages/
│   ├── HomePage.tsx (updated)
│   ├── AchievementsPage.tsx (new)
│   ├── ProfilePage.tsx (new)
│   └── ComponentShowcase.tsx (new)
├── utils/
│   └── designTokens.ts (new)
├── routes/
│   └── index.tsx (updated)
└── index.css (updated)
```

## Browser Compatibility

- Modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- Mobile browsers (iOS Safari 14+, Chrome Mobile 90+)
- Telegram WebView (all versions supporting Telegram Mini Apps)

## Performance Considerations

1. **Lazy Loading:** Components can be lazy-loaded if needed
2. **Animations:** Optimized with Framer Motion's hardware acceleration
3. **Bundle Size:** Tree-shaking friendly exports
4. **CSS:** Purged unused Tailwind classes in production

## Future Enhancements

Potential improvements:
1. Unit tests for all components
2. Storybook integration (alternative to showcase page)
3. Additional components (Modal, Dropdown, Input, etc.)
4. Animation customization props
5. Theme customization beyond Telegram tokens
6. Accessibility audit and improvements
7. Performance monitoring

## Acceptance Criteria ✓

- ✅ Reusable UI primitives (buttons, cards, badges, progress bars)
- ✅ Aligned with design tokens (Telegram theme variables)
- ✅ Bottom navigation component with 3 sections (Курс, Достижения, Профиль)
- ✅ Iconography (lucide-react icons)
- ✅ Animations/transitions using Framer Motion
- ✅ Showcase page documenting components
- ✅ Responsive on mobile
- ✅ Meets design spec (Telegram design system)
- ✅ Documented (this file + README.md)
- ✅ Ready for lint/tests

## Support

For questions or issues, refer to:
- Component README: `src/components/ui/README.md`
- Live showcase: Navigate to `/showcase` in the app
- Design tokens: `src/utils/designTokens.ts`
