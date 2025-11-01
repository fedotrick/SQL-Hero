export const HomePage = () => {
  return (
    <div className="p-4">
      <div className="space-y-6">
        <section className="rounded-lg bg-telegram-section-bg p-6 shadow-sm">
          <h2 className="mb-3 text-2xl font-bold text-telegram-text">
            Welcome to Telegram Mini App
          </h2>
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
      </div>
    </div>
  );
};
