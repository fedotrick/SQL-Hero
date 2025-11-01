import type { TelegramWebApp, TelegramWebAppInstance } from "../types/telegram";

class TelegramService {
  private webApp: TelegramWebAppInstance = undefined;

  constructor() {
    if (typeof window !== "undefined" && window.Telegram?.WebApp) {
      this.webApp = window.Telegram.WebApp as TelegramWebApp;
    }
  }

  isAvailable(): boolean {
    return this.webApp !== undefined;
  }

  getWebApp(): TelegramWebApp | null {
    return this.webApp || null;
  }

  getInitData(): string {
    if (!this.webApp) {
      throw new Error("Telegram WebApp is not available");
    }
    return this.webApp.initData;
  }

  getInitDataUnsafe() {
    if (!this.webApp) {
      throw new Error("Telegram WebApp is not available");
    }
    return this.webApp.initDataUnsafe;
  }

  ready(): void {
    if (this.webApp) {
      this.webApp.ready();
    }
  }

  expand(): void {
    if (this.webApp) {
      this.webApp.expand();
    }
  }

  close(): void {
    if (this.webApp) {
      this.webApp.close();
    }
  }

  showAlert(message: string): Promise<void> {
    return new Promise((resolve) => {
      if (this.webApp) {
        this.webApp.showAlert(message, () => resolve());
      } else {
        alert(message);
        resolve();
      }
    });
  }

  showConfirm(message: string): Promise<boolean> {
    return new Promise((resolve) => {
      if (this.webApp) {
        this.webApp.showConfirm(message, (confirmed) => resolve(confirmed));
      } else {
        resolve(confirm(message));
      }
    });
  }

  openLink(url: string, options?: { try_instant_view?: boolean }): void {
    if (this.webApp) {
      this.webApp.openLink(url, options);
    } else {
      window.open(url, "_blank");
    }
  }

  getColorScheme(): "light" | "dark" {
    return this.webApp?.colorScheme || "light";
  }

  getThemeParams() {
    return this.webApp?.themeParams || {};
  }

  getPlatform(): string {
    return this.webApp?.platform || "unknown";
  }

  getVersion(): string {
    return this.webApp?.version || "unknown";
  }
}

export const telegramService = new TelegramService();
