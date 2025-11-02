import type { AchievementsListResponse } from "../types/achievements";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export class AchievementsError extends Error {
  statusCode?: number;

  constructor(message: string, statusCode?: number) {
    super(message);
    this.name = "AchievementsError";
    this.statusCode = statusCode;
  }
}

class AchievementsService {
  async getAchievements(token: string): Promise<AchievementsListResponse> {
    try {
      const response = await fetch(`${API_URL}/achievements`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          detail: "Failed to fetch achievements",
        }));
        throw new AchievementsError(
          errorData.detail || `Request failed with status ${response.status}`,
          response.status
        );
      }

      const data: AchievementsListResponse = await response.json();
      return data;
    } catch (error) {
      if (error instanceof AchievementsError) {
        throw error;
      }
      if (error instanceof Error) {
        throw new AchievementsError(`Network error: ${error.message}`);
      }
      throw new AchievementsError("Unknown error fetching achievements");
    }
  }
}

export const achievementsService = new AchievementsService();
