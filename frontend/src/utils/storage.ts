const TOKEN_KEY = "telegram_auth_token";
const USER_KEY = "telegram_user";

export const storage = {
  getToken: (): string | null => {
    try {
      return localStorage.getItem(TOKEN_KEY);
    } catch (error) {
      console.error("Failed to get token from storage:", error);
      return null;
    }
  },

  setToken: (token: string): void => {
    try {
      localStorage.setItem(TOKEN_KEY, token);
    } catch (error) {
      console.error("Failed to set token in storage:", error);
    }
  },

  removeToken: (): void => {
    try {
      localStorage.removeItem(TOKEN_KEY);
    } catch (error) {
      console.error("Failed to remove token from storage:", error);
    }
  },

  getUser: (): unknown => {
    try {
      const userStr = localStorage.getItem(USER_KEY);
      return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
      console.error("Failed to get user from storage:", error);
      return null;
    }
  },

  setUser: (user: unknown): void => {
    try {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    } catch (error) {
      console.error("Failed to set user in storage:", error);
    }
  },

  removeUser: (): void => {
    try {
      localStorage.removeItem(USER_KEY);
    } catch (error) {
      console.error("Failed to remove user from storage:", error);
    }
  },

  clear: (): void => {
    try {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    } catch (error) {
      console.error("Failed to clear storage:", error);
    }
  },
};
