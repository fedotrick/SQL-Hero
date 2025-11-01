import { installMockTelegramWebApp, uninstallMockTelegramWebApp } from "../mocks/telegramWebApp";

export const enableMockTelegram = (): void => {
  installMockTelegramWebApp();
  console.log("%c[Dev Tools] Mock Telegram WebApp enabled", "color: #3390ec; font-weight: bold");
  console.log("%cYou can now test the app as if it's running inside Telegram", "color: #999");
  console.log("%cTo disable mock mode, call window.disableMockTelegram()", "color: #999");
};

export const disableMockTelegram = (): void => {
  uninstallMockTelegramWebApp();
  console.log("%c[Dev Tools] Mock Telegram WebApp disabled", "color: #f44; font-weight: bold");
};

if (typeof window !== "undefined" && import.meta.env.DEV) {
  (window as unknown as Record<string, unknown>).enableMockTelegram = enableMockTelegram;
  (window as unknown as Record<string, unknown>).disableMockTelegram = disableMockTelegram;

  console.log("%c🚀 Dev Tools Available", "color: #3390ec; font-weight: bold; font-size: 14px");
  console.log(
    "%cUse window.enableMockTelegram() to test Telegram integration without Telegram",
    "color: #999"
  );
}
