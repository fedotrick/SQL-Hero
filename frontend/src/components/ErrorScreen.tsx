interface ErrorScreenProps {
  error: string;
  onRetry?: () => void;
}

export const ErrorScreen = ({ error, onRetry }: ErrorScreenProps) => {
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
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </div>
        </div>

        <div className="space-y-3 text-center">
          <h1 className="text-2xl font-bold text-telegram-text">Authentication Failed</h1>
          <p className="text-telegram-subtitle">{error}</p>
        </div>

        {onRetry && (
          <button
            onClick={onRetry}
            className="w-full rounded-lg bg-telegram-button px-4 py-3 text-telegram-button-text transition-opacity hover:opacity-90"
          >
            Try Again
          </button>
        )}

        <div className="border-t border-telegram-section-separator pt-4 text-center">
          <p className="text-xs text-telegram-hint">
            If the problem persists, please contact support.
          </p>
        </div>
      </div>
    </div>
  );
};
