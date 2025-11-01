import { useAuthStore } from "../store/authStore";
import { telegramHaptics } from "../services/telegramHaptics";
import { telegramService } from "../services/telegram";

export const HomePage = () => {
  const { user } = useAuthStore();

  const handleHapticClick = (
    type: "light" | "medium" | "heavy" | "success" | "error" | "warning"
  ) => {
    switch (type) {
      case "light":
        telegramHaptics.light();
        break;
      case "medium":
        telegramHaptics.medium();
        break;
      case "heavy":
        telegramHaptics.heavy();
        break;
      case "success":
        telegramHaptics.success();
        break;
      case "error":
        telegramHaptics.error();
        break;
      case "warning":
        telegramHaptics.warning();
        break;
    }
  };

  return (
    <div className="p-4">
      <div className="space-y-6">
        <section className="rounded-lg bg-telegram-section-bg p-6 shadow-sm">
          <h2 className="mb-3 text-2xl font-bold text-telegram-text">
            Welcome to Telegram Mini App
          </h2>
          {user && (
            <div className="mb-3 rounded-lg bg-telegram-secondary-bg p-4">
              <p className="mb-2 text-sm font-semibold text-telegram-text">Authenticated as:</p>
              <p className="text-telegram-subtitle">
                {user.first_name} {user.last_name}
                {user.username && ` (@${user.username})`}
              </p>
              <p className="mt-1 text-xs text-telegram-hint">Telegram ID: {user.telegram_id}</p>
            </div>
          )}
          <p className="text-telegram-subtitle">
            This is a React + TypeScript application configured for Telegram mini-apps with
            constrained viewport (max-width: 480px).
          </p>
        </section>

        <section className="rounded-lg bg-telegram-section-bg p-6 shadow-sm">
          <h3 className="mb-3 text-lg font-semibold text-telegram-text">Features</h3>
          <ul className="space-y-2">
            <li className="flex items-start">
              <span className="mr-2 text-telegram-accent-text">✓</span>
              <span className="text-telegram-subtitle">Tailwind CSS with Telegram theme</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2 text-telegram-accent-text">✓</span>
              <span className="text-telegram-subtitle">React Router for navigation</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2 text-telegram-accent-text">✓</span>
              <span className="text-telegram-subtitle">React Query for data fetching</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2 text-telegram-accent-text">✓</span>
              <span className="text-telegram-subtitle">Zustand for state management</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2 text-telegram-accent-text">✓</span>
              <span className="text-telegram-subtitle">Dark/Light theme support</span>
            </li>
          </ul>
        </section>

        <section className="rounded-lg bg-telegram-section-bg p-6 shadow-sm">
          <h3 className="mb-3 text-lg font-semibold text-telegram-text">Typography</h3>
          <div className="space-y-2">
            <p className="text-sm text-telegram-hint">Small hint text</p>
            <p className="text-telegram-subtitle">Subtitle text</p>
            <p className="text-telegram-text">Regular body text</p>
            <p className="font-semibold text-telegram-text">Bold text</p>
            <a href="#" className="text-telegram-link underline">
              Link text
            </a>
          </div>
        </section>

        <section className="rounded-lg bg-telegram-section-bg p-6 shadow-sm">
          <h3 className="mb-3 text-lg font-semibold text-telegram-text">Buttons</h3>
          <div className="flex flex-wrap gap-3">
            <button className="rounded-lg bg-telegram-button px-4 py-2 text-telegram-button-text transition-opacity hover:opacity-90">
              Primary Button
            </button>
            <button className="rounded-lg border border-telegram-section-separator px-4 py-2 text-telegram-text transition-colors hover:bg-telegram-secondary-bg">
              Secondary Button
            </button>
            <button className="rounded-lg bg-telegram-destructive px-4 py-2 text-white transition-opacity hover:opacity-90">
              Destructive Button
            </button>
          </div>
        </section>

        <section className="rounded-lg bg-telegram-section-bg p-6 shadow-sm">
          <h3 className="mb-3 text-lg font-semibold text-telegram-text">Haptic Feedback Demo</h3>
          <p className="mb-4 text-sm text-telegram-subtitle">
            Try these buttons to feel haptic feedback (only works in Telegram)
          </p>
          <div className="space-y-3">
            <div>
              <p className="mb-2 text-sm font-semibold text-telegram-text">Impact Styles:</p>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => handleHapticClick("light")}
                  className="rounded-lg border border-telegram-section-separator px-3 py-2 text-sm text-telegram-text transition-colors hover:bg-telegram-secondary-bg"
                >
                  Light
                </button>
                <button
                  onClick={() => handleHapticClick("medium")}
                  className="rounded-lg border border-telegram-section-separator px-3 py-2 text-sm text-telegram-text transition-colors hover:bg-telegram-secondary-bg"
                >
                  Medium
                </button>
                <button
                  onClick={() => handleHapticClick("heavy")}
                  className="rounded-lg border border-telegram-section-separator px-3 py-2 text-sm text-telegram-text transition-colors hover:bg-telegram-secondary-bg"
                >
                  Heavy
                </button>
              </div>
            </div>
            <div>
              <p className="mb-2 text-sm font-semibold text-telegram-text">Notifications:</p>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => handleHapticClick("success")}
                  className="rounded-lg bg-green-600 px-3 py-2 text-sm text-white transition-opacity hover:opacity-90"
                >
                  Success
                </button>
                <button
                  onClick={() => handleHapticClick("error")}
                  className="rounded-lg bg-telegram-destructive px-3 py-2 text-sm text-white transition-opacity hover:opacity-90"
                >
                  Error
                </button>
                <button
                  onClick={() => handleHapticClick("warning")}
                  className="rounded-lg bg-yellow-600 px-3 py-2 text-sm text-white transition-opacity hover:opacity-90"
                >
                  Warning
                </button>
              </div>
            </div>
          </div>
        </section>

        <section className="rounded-lg bg-telegram-section-bg p-6 shadow-sm">
          <h3 className="mb-3 text-lg font-semibold text-telegram-text">Telegram WebApp Info</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-telegram-hint">Platform:</span>
              <span className="text-telegram-text">{telegramService.getPlatform()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-telegram-hint">Version:</span>
              <span className="text-telegram-text">{telegramService.getVersion()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-telegram-hint">Color Scheme:</span>
              <span className="text-telegram-text">{telegramService.getColorScheme()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-telegram-hint">Available:</span>
              <span className="text-telegram-text">
                {telegramService.isAvailable() ? "Yes" : "No"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-telegram-hint">Haptics Available:</span>
              <span className="text-telegram-text">
                {telegramHaptics.isAvailable() ? "Yes" : "No"}
              </span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};
