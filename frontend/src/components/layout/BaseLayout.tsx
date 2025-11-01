import type { ReactNode } from "react";
import { useThemeStore } from "../../store/themeStore";
import { useTelegramWebApp } from "../../hooks/useTelegramWebApp";
import { BottomNavigation } from "../ui/BottomNavigation";

interface BaseLayoutProps {
  children: ReactNode;
}

export const BaseLayout = ({ children }: BaseLayoutProps) => {
  const { theme, toggleTheme } = useThemeStore();
  useTelegramWebApp();

  return (
    <div className="min-h-screen bg-telegram-bg text-telegram-text">
      <div className="mx-auto max-w-telegram">
        <header className="bg-telegram-header-bg border-b border-telegram-section-separator">
          <div className="flex items-center justify-between px-4 py-3">
            <h1 className="text-xl font-semibold">Telegram Mini App</h1>
            <button
              onClick={toggleTheme}
              className="rounded-lg bg-telegram-button px-3 py-2 text-sm text-telegram-button-text transition-opacity hover:opacity-90"
              aria-label="Toggle theme"
            >
              {theme === "light" ? "🌙" : "☀️"}
            </button>
          </div>
        </header>
        <main className="min-h-[calc(100vh-64px)]">{children}</main>
        <BottomNavigation />
      </div>
    </div>
  );
};
