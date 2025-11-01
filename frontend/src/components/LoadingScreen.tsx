export const LoadingScreen = () => {
  return (
    <div className="flex min-h-screen items-center justify-center bg-telegram-bg">
      <div className="text-center">
        <div className="mb-4 flex justify-center">
          <div className="h-16 w-16 animate-spin rounded-full border-4 border-telegram-section-separator border-t-telegram-button"></div>
        </div>
        <p className="text-lg text-telegram-subtitle">Authenticating...</p>
        <p className="mt-2 text-sm text-telegram-hint">Please wait a moment</p>
      </div>
    </div>
  );
};
