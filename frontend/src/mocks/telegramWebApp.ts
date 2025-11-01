import type { TelegramWebApp } from "../types/telegram";

const mockUser = {
  id: 123456789,
  first_name: "Test",
  last_name: "User",
  username: "testuser",
  language_code: "en",
  is_premium: false,
};

const mockInitDataUnsafe = {
  user: mockUser,
  auth_date: Math.floor(Date.now() / 1000),
  hash: "mock_hash_for_testing",
};

const mockInitData = `user=${encodeURIComponent(JSON.stringify(mockUser))}&auth_date=${mockInitDataUnsafe.auth_date}&hash=${mockInitDataUnsafe.hash}`;

export const createMockTelegramWebApp = (
  overrides: Partial<TelegramWebApp> = {}
): TelegramWebApp => {
  const mock: TelegramWebApp = {
    initData: mockInitData,
    initDataUnsafe: mockInitDataUnsafe,
    version: "7.0",
    platform: "mock",
    colorScheme: "light",
    themeParams: {
      bg_color: "#ffffff",
      text_color: "#000000",
      hint_color: "#999999",
      link_color: "#3390ec",
      button_color: "#3390ec",
      button_text_color: "#ffffff",
      secondary_bg_color: "#f4f4f5",
    },
    isExpanded: true,
    viewportHeight: 600,
    viewportStableHeight: 600,
    headerColor: "#ffffff",
    backgroundColor: "#ffffff",
    isClosingConfirmationEnabled: false,
    BackButton: {
      isVisible: false,
      onClick: (callback) => {
        console.log("Mock BackButton.onClick registered", callback);
      },
      offClick: (callback) => {
        console.log("Mock BackButton.offClick registered", callback);
      },
      show: () => {
        console.log("Mock BackButton.show called");
      },
      hide: () => {
        console.log("Mock BackButton.hide called");
      },
    },
    MainButton: {
      text: "",
      color: "#3390ec",
      textColor: "#ffffff",
      isVisible: false,
      isActive: true,
      isProgressVisible: false,
      setText: (text) => {
        console.log("Mock MainButton.setText called with:", text);
      },
      onClick: (callback) => {
        console.log("Mock MainButton.onClick registered", callback);
      },
      offClick: (callback) => {
        console.log("Mock MainButton.offClick registered", callback);
      },
      show: () => {
        console.log("Mock MainButton.show called");
      },
      hide: () => {
        console.log("Mock MainButton.hide called");
      },
      enable: () => {
        console.log("Mock MainButton.enable called");
      },
      disable: () => {
        console.log("Mock MainButton.disable called");
      },
      showProgress: (leaveActive) => {
        console.log("Mock MainButton.showProgress called with:", leaveActive);
      },
      hideProgress: () => {
        console.log("Mock MainButton.hideProgress called");
      },
    },
    HapticFeedback: {
      impactOccurred: (style) => {
        console.log(`Mock HapticFeedback.impactOccurred called with style: ${style}`);
      },
      notificationOccurred: (type) => {
        console.log(`Mock HapticFeedback.notificationOccurred called with type: ${type}`);
      },
      selectionChanged: () => {
        console.log("Mock HapticFeedback.selectionChanged called");
      },
    },
    ready: () => {
      console.log("Mock Telegram WebApp ready");
    },
    expand: () => {
      console.log("Mock Telegram WebApp expand");
    },
    close: () => {
      console.log("Mock Telegram WebApp close");
    },
    sendData: (data) => {
      console.log("Mock Telegram WebApp sendData:", data);
    },
    openLink: (url, options) => {
      console.log("Mock Telegram WebApp openLink:", url, options);
      window.open(url, "_blank");
    },
    openTelegramLink: (url) => {
      console.log("Mock Telegram WebApp openTelegramLink:", url);
    },
    openInvoice: (url, callback) => {
      console.log("Mock Telegram WebApp openInvoice:", url);
      callback?.("paid");
    },
    showPopup: (params, callback) => {
      console.log("Mock Telegram WebApp showPopup:", params);
      setTimeout(() => callback?.("ok"), 100);
    },
    showAlert: (message, callback) => {
      console.log("Mock Telegram WebApp showAlert:", message);
      alert(message);
      callback?.();
    },
    showConfirm: (message, callback) => {
      console.log("Mock Telegram WebApp showConfirm:", message);
      const confirmed = confirm(message);
      callback?.(confirmed);
    },
    showScanQrPopup: (params, callback) => {
      console.log("Mock Telegram WebApp showScanQrPopup:", params);
      return callback?.("mock_qr_data") || false;
    },
    closeScanQrPopup: () => {
      console.log("Mock Telegram WebApp closeScanQrPopup");
    },
    readTextFromClipboard: (callback) => {
      console.log("Mock Telegram WebApp readTextFromClipboard");
      callback?.("mock clipboard text");
    },
    requestWriteAccess: (callback) => {
      console.log("Mock Telegram WebApp requestWriteAccess");
      callback?.(true);
    },
    requestContact: (callback) => {
      console.log("Mock Telegram WebApp requestContact");
      callback?.(true, { contact: mockUser });
    },
    onEvent: (eventType, callback) => {
      console.log(`Mock Telegram WebApp onEvent: ${eventType}`, callback);
    },
    offEvent: (eventType, callback) => {
      console.log(`Mock Telegram WebApp offEvent: ${eventType}`, callback);
    },
    ...overrides,
  };

  return mock;
};

export const installMockTelegramWebApp = (overrides: Partial<TelegramWebApp> = {}): void => {
  if (typeof window !== "undefined") {
    const mockWebApp = createMockTelegramWebApp(overrides);
    window.Telegram = {
      WebApp: mockWebApp,
    };
    console.log("Mock Telegram WebApp installed");
  }
};

export const uninstallMockTelegramWebApp = (): void => {
  if (typeof window !== "undefined") {
    delete window.Telegram;
    console.log("Mock Telegram WebApp uninstalled");
  }
};
