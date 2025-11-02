import type { LeaderboardResponse } from "../types/leaderboard";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export class LeaderboardError extends Error {
  statusCode?: number;

  constructor(message: string, statusCode?: number) {
    super(message);
    this.name = "LeaderboardError";
    this.statusCode = statusCode;
  }
}

class LeaderboardService {
  private async makeRequest<T>(endpoint: string, token: string): Promise<T> {
    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          detail: "Request failed",
        }));
        throw new LeaderboardError(
          errorData.detail || `Request failed with status ${response.status}`,
          response.status
        );
      }

      return response.json();
    } catch (error) {
      if (error instanceof LeaderboardError) {
        throw error;
      }
      if (error instanceof Error) {
        throw new LeaderboardError(`Network error: ${error.message}`);
      }
      throw new LeaderboardError("Unknown error");
    }
  }

  async getLeaderboard(token: string, limit = 100): Promise<LeaderboardResponse> {
    return this.makeRequest<LeaderboardResponse>(`/leaderboard?limit=${limit}`, token);
  }
}

export const leaderboardService = new LeaderboardService();
