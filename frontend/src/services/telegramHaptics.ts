import { telegramService } from "./telegram";

type ImpactStyle = "light" | "medium" | "heavy" | "rigid" | "soft";
type NotificationType = "error" | "success" | "warning";

class TelegramHapticsService {
  private isEnabled = true;

  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
  }

  isAvailable(): boolean {
    const webApp = telegramService.getWebApp();
    return webApp?.HapticFeedback !== undefined;
  }

  impactOccurred(style: ImpactStyle = "medium"): void {
    if (!this.isEnabled || !this.isAvailable()) {
      console.debug(`[Haptics] Impact feedback (${style}) - not available`);
      return;
    }

    try {
      const webApp = telegramService.getWebApp();
      webApp?.HapticFeedback.impactOccurred(style);
      console.debug(`[Haptics] Impact feedback (${style}) - triggered`);
    } catch (error) {
      console.error("Failed to trigger impact haptic feedback:", error);
    }
  }

  notificationOccurred(type: NotificationType): void {
    if (!this.isEnabled || !this.isAvailable()) {
      console.debug(`[Haptics] Notification feedback (${type}) - not available`);
      return;
    }

    try {
      const webApp = telegramService.getWebApp();
      webApp?.HapticFeedback.notificationOccurred(type);
      console.debug(`[Haptics] Notification feedback (${type}) - triggered`);
    } catch (error) {
      console.error("Failed to trigger notification haptic feedback:", error);
    }
  }

  selectionChanged(): void {
    if (!this.isEnabled || !this.isAvailable()) {
      console.debug("[Haptics] Selection changed feedback - not available");
      return;
    }

    try {
      const webApp = telegramService.getWebApp();
      webApp?.HapticFeedback.selectionChanged();
      console.debug("[Haptics] Selection changed feedback - triggered");
    } catch (error) {
      console.error("Failed to trigger selection changed haptic feedback:", error);
    }
  }

  light(): void {
    this.impactOccurred("light");
  }

  medium(): void {
    this.impactOccurred("medium");
  }

  heavy(): void {
    this.impactOccurred("heavy");
  }

  success(): void {
    this.notificationOccurred("success");
  }

  error(): void {
    this.notificationOccurred("error");
  }

  warning(): void {
    this.notificationOccurred("warning");
  }
}

export const telegramHaptics = new TelegramHapticsService();
