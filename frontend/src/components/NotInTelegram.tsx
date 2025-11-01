export const NotInTelegram = () => {
  return (
    <div className="flex min-h-screen items-center justify-center bg-telegram-bg p-4">
      <div className="max-w-md space-y-6 rounded-lg bg-telegram-section-bg p-8 shadow-lg">
        <div className="flex justify-center">
          <div className="flex h-20 w-20 items-center justify-center rounded-full bg-telegram-destructive/10">
            <svg
              className="h-10 w-10 text-telegram-destructive"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
        </div>

        <div className="space-y-3 text-center">
          <h1 className="text-2xl font-bold text-telegram-text">Not Available</h1>
          <p className="text-telegram-subtitle">
            This application must be opened through Telegram.
          </p>
        </div>

        <div className="rounded-lg bg-telegram-secondary-bg p-4">
          <h2 className="mb-2 text-sm font-semibold text-telegram-text">How to use:</h2>
          <ol className="space-y-2 text-sm text-telegram-subtitle">
            <li className="flex items-start">
              <span className="mr-2 font-semibold text-telegram-accent-text">1.</span>
              <span>Open Telegram on your device</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2 font-semibold text-telegram-accent-text">2.</span>
              <span>Find the bot that provides this mini app</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2 font-semibold text-telegram-accent-text">3.</span>
              <span>Launch the mini app from within Telegram</span>
            </li>
          </ol>
        </div>

        <div className="border-t border-telegram-section-separator pt-4 text-center">
          <p className="text-xs text-telegram-hint">
            This security measure ensures your data is protected.
          </p>
        </div>
      </div>
    </div>
  );
};
