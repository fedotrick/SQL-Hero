# Frontend Setup Documentation

## Overview

This is a React + TypeScript application configured for Telegram Mini Apps with Vite as the build tool.

## Tech Stack

- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite 7
- **Styling**: Tailwind CSS 3.x with Telegram theme support
- **State Management**:
  - Zustand for client state
  - React Query for server state
- **Routing**: React Router v7
- **Code Quality**:
  - ESLint for linting
  - Prettier for formatting
  - Husky for pre-commit hooks
  - Stylelint for CSS linting

## Features

### Telegram Mini App Integration

- Configured viewport for Telegram mini-apps (max-width: 480px)
- Telegram Web App SDK integration
- Theme syncing with Telegram app
- Dark/Light theme support with automatic detection

### Tailwind CSS Configuration

Custom Telegram theme colors accessible via Tailwind utilities:

- `bg-telegram-bg` - Background color
- `text-telegram-text` - Primary text color
- `text-telegram-hint` - Hint text color
- `text-telegram-link` - Link color
- `bg-telegram-button` - Button background
- `text-telegram-button-text` - Button text color
- And more...

### Base Layout

The `BaseLayout` component provides:

- Constrained viewport (max-width: 480px)
- Theme toggle button
- Telegram Web App integration
- Responsive header

## Project Structure

```
src/
├── components/
│   └── layout/
│       ├── BaseLayout.tsx    # Main layout wrapper
│       └── index.ts
├── hooks/
│   └── useTelegramWebApp.ts  # Telegram Web App SDK hook
├── pages/
│   └── HomePage.tsx          # Example home page
├── routes/
│   └── index.tsx             # Router configuration
├── store/
│   ├── themeStore.ts         # Theme state management
│   └── index.ts
├── utils/
│   └── queryClient.ts        # React Query configuration
├── App.tsx                   # Main app component
├── main.tsx                  # Entry point
└── index.css                 # Global styles with Telegram theme
```

## Available Scripts

- `pnpm dev` - Start development server
- `pnpm build` - Build for production
- `pnpm lint` - Run ESLint
- `pnpm lint:style` - Run Stylelint
- `pnpm format` - Format code with Prettier
- `pnpm format:check` - Check code formatting
- `pnpm preview` - Preview production build

## Development

1. Install dependencies:

   ```bash
   pnpm install
   ```

2. Start development server:

   ```bash
   pnpm dev
   ```

3. The app will be available at `http://localhost:5173`

## Theme System

The application uses CSS custom properties for theming, allowing seamless integration with Telegram's theme system:

- **Light Theme**: Default theme with bright backgrounds
- **Dark Theme**: Dark backgrounds activated via `.dark` class
- **Telegram Integration**: Auto-syncs with Telegram app theme when loaded as a mini-app

## Viewport Constraints

The app is optimized for Telegram mini-app viewport:

- Maximum width: 480px
- Centered layout on larger screens
- Mobile-first responsive design
- Touch-optimized interactions

## Pre-commit Hooks

Husky is configured to run quality checks before commits:

- ESLint validation
- Prettier format checking

These checks ensure code quality and consistency across the codebase.
