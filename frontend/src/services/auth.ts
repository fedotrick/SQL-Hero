const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface TelegramAuthRequest {
  init_data: string;
}

export interface UserProfile {
  id: number;
  telegram_id: number;
  username: string | null;
  first_name: string | null;
  last_name: string | null;
  language_code: string | null;
  is_active: boolean;
  last_active_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface TelegramAuthResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
}

export class AuthError extends Error {
  statusCode?: number;

  constructor(message: string, statusCode?: number) {
    super(message);
    this.name = "AuthError";
    this.statusCode = statusCode;
  }
}

class AuthService {
  async authenticateWithTelegram(initData: string): Promise<TelegramAuthResponse> {
    if (!initData || initData.trim() === "") {
      throw new AuthError("Init data is empty or invalid");
    }

    try {
      const response = await fetch(`${API_URL}/auth/telegram`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ init_data: initData } as TelegramAuthRequest),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          detail: "Authentication failed",
        }));
        throw new AuthError(
          errorData.detail || `Authentication failed with status ${response.status}`,
          response.status
        );
      }

      const data: TelegramAuthResponse = await response.json();
      return data;
    } catch (error) {
      if (error instanceof AuthError) {
        throw error;
      }
      if (error instanceof Error) {
        throw new AuthError(`Network error: ${error.message}`);
      }
      throw new AuthError("Unknown authentication error");
    }
  }

  async makeAuthenticatedRequest<T>(
    endpoint: string,
    token: string,
    options?: RequestInit
  ): Promise<T> {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        ...options?.headers,
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    return response.json();
  }
}

export const authService = new AuthService();
