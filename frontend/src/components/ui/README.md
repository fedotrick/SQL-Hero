# UI Components Library

A collection of reusable UI primitives built with React, TypeScript, Tailwind CSS, and Framer Motion. All components are aligned with Telegram design tokens and support both light and dark themes.

## Components

### Button

Versatile button component with multiple variants, sizes, and states.

**Variants:**

- `primary` - Primary action button (default)
- `secondary` - Secondary actions
- `outline` - Outlined style
- `ghost` - Minimal style
- `destructive` - For destructive actions

**Sizes:**

- `sm` - Small (text-sm, px-3 py-1.5)
- `md` - Medium (text-base, px-4 py-2) (default)
- `lg` - Large (text-lg, px-6 py-3)

**Props:**

- `variant?: ButtonVariant` - Button style variant
- `size?: ButtonSize` - Button size
- `fullWidth?: boolean` - Make button full width
- `leftIcon?: React.ReactNode` - Icon on the left
- `rightIcon?: React.ReactNode` - Icon on the right
- `isLoading?: boolean` - Show loading spinner
- All standard button HTML attributes

**Usage:**

```tsx
import { Button } from "@/components/ui";
import { Plus } from "lucide-react";

<Button variant="primary" size="md" leftIcon={<Plus size={16} />}>
  Add Item
</Button>;
```

### Card

Container component for grouping related content.

**Variants:**

- `default` - Standard background
- `elevated` - With shadow
- `outlined` - With border

**Padding:**

- `none` - No padding
- `sm` - Small padding (p-3)
- `md` - Medium padding (p-4) (default)
- `lg` - Large padding (p-6)

**Props:**

- `variant?: CardVariant` - Card style variant
- `padding?: CardPadding` - Padding size
- `interactive?: boolean` - Add hover effects

**Subcomponents:**

- `CardHeader` - Header section
- `CardTitle` - Title component
- `CardContent` - Main content area

**Usage:**

```tsx
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui";

<Card variant="elevated" interactive>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
  </CardHeader>
  <CardContent>Card content goes here</CardContent>
</Card>;
```

### Badge

Small labels for displaying metadata, status, or categories.

**Variants:**

- `default` - Default style
- `success` - Success/positive state
- `warning` - Warning state
- `error` - Error/danger state
- `info` - Info state
- `outline` - Outlined style

**Sizes:**

- `sm` - Small (text-xs, px-2 py-0.5)
- `md` - Medium (text-sm, px-2.5 py-1) (default)
- `lg` - Large (text-base, px-3 py-1.5)

**Props:**

- `variant?: BadgeVariant` - Badge style variant
- `size?: BadgeSize` - Badge size
- `dot?: boolean` - Show dot indicator

**Usage:**

```tsx
import { Badge } from "@/components/ui";

<Badge variant="success" dot>
  Active
</Badge>;
```

### ProgressBar

Linear and circular progress indicators.

**Variants:**

- `default` - Uses theme button color
- `success` - Green color
- `warning` - Yellow color
- `error` - Red color

**Sizes (Linear):**

- `sm` - Small (h-1)
- `md` - Medium (h-2) (default)
- `lg` - Large (h-3)

**Props (ProgressBar):**

- `value: number` - Current progress value (required)
- `max?: number` - Maximum value (default: 100)
- `size?: ProgressBarSize` - Bar size
- `variant?: ProgressBarVariant` - Color variant
- `showLabel?: boolean` - Show percentage label
- `label?: string` - Custom label text
- `animated?: boolean` - Enable animation (default: true)

**Props (CircularProgress):**

- `value: number` - Current progress value (required)
- `max?: number` - Maximum value (default: 100)
- `size?: number` - Circle size in pixels (default: 64)
- `strokeWidth?: number` - Stroke width (default: 4)
- `variant?: ProgressBarVariant` - Color variant
- `showLabel?: boolean` - Show percentage label (default: true)

**Usage:**

```tsx
import { ProgressBar, CircularProgress } from "@/components/ui";

<ProgressBar value={65} showLabel label="Course Progress" />
<CircularProgress value={75} size={80} variant="success" />
```

### BottomNavigation

Fixed bottom navigation bar for mobile apps with smooth animations.

**Features:**

- Fixed positioning at bottom
- Animated active indicator
- Icons with labels
- Smooth transitions
- Safe area support for notched devices

**Navigation Items:**

- Курс (Course) - BookOpen icon
- Достижения (Achievements) - Trophy icon
- Профиль (Profile) - User icon

**Props:**

- `className?: string` - Additional CSS classes

**Usage:**

```tsx
import { BottomNavigation } from "@/components/ui";

<BottomNavigation />;
```

## Design Tokens

All components use design tokens from `/src/utils/designTokens.ts`:

- **Colors** - Telegram theme colors via CSS variables
- **Spacing** - xs, sm, md, lg, xl, 2xl
- **Border Radius** - sm, md, lg, xl, full
- **Font Size** - xs, sm, base, lg, xl, 2xl, 3xl
- **Font Weight** - normal, medium, semibold, bold
- **Shadows** - sm, md, lg
- **Transitions** - fast (150ms), base (200ms), slow (300ms)

## Animations

Components use Framer Motion for smooth, performant animations:

- **Button** - Scale on tap
- **Card** - Hover and tap effects when interactive
- **Badge** - Fade in with scale
- **ProgressBar** - Smooth fill animation
- **BottomNavigation** - Active indicator slide animation

## Accessibility

All components follow accessibility best practices:

- Semantic HTML
- Proper ARIA attributes
- Keyboard navigation support
- Focus management
- Screen reader friendly

## Responsive Design

Components are optimized for mobile-first design with:

- Flexible layouts
- Touch-friendly sizes
- Responsive typography
- Mobile viewport constraints (max-width: 480px for Telegram)

## Dark Mode

All components automatically support dark mode through Telegram theme variables:

- Light theme: Default Telegram light colors
- Dark theme: Telegram dark colors
- Automatic switching based on user preference

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Telegram WebView

## Dependencies

- `react` - UI framework
- `framer-motion` - Animation library
- `lucide-react` - Icon library
- `tailwindcss` - Utility-first CSS framework
- `react-router-dom` - Routing (for BottomNavigation)
