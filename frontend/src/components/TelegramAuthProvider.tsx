import { useEffect, useCallback, type ReactNode } from "react";
import { useAuthStore } from "../store/authStore";
import { telegramService } from "../services/telegram";
import { authService } from "../services/auth";
import { LoadingScreen } from "./LoadingScreen";
import { ErrorScreen } from "./ErrorScreen";
import { NotInTelegram } from "./NotInTelegram";

interface TelegramAuthProviderProps {
  children: ReactNode;
}

export const TelegramAuthProvider = ({ children }: TelegramAuthProviderProps) => {
  const { status, error, setLoading, setAuthenticated, setError, setNotInTelegram, initialize } =
    useAuthStore();

  const authenticate = useCallback(async () => {
    try {
      setLoading();

      if (!telegramService.isAvailable()) {
        setNotInTelegram();
        return;
      }

      telegramService.ready();

      const initData = telegramService.getInitData();

      if (!initData || initData.trim() === "") {
        setNotInTelegram();
        return;
      }

      const response = await authService.authenticateWithTelegram(initData);
      setAuthenticated(response.access_token, response.user);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "An unknown error occurred during authentication";
      setError(message);
    }
  }, [setLoading, setAuthenticated, setError, setNotInTelegram]);

  useEffect(() => {
    initialize();

    if (status === "idle") {
      authenticate();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (status === "loading") {
    return <LoadingScreen />;
  }

  if (status === "not-in-telegram") {
    return <NotInTelegram />;
  }

  if (status === "error") {
    return <ErrorScreen error={error || "Unknown error"} onRetry={authenticate} />;
  }

  if (status === "authenticated") {
    return <>{children}</>;
  }

  return <LoadingScreen />;
};
