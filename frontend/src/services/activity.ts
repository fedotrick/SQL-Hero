import {
  ActivityCalendarResponse,
  ActivityHeatmapResponse,
  DailyActivityStats,
  StreakData,
} from "../types/activity";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const activityService = {
  async getCalendarData(
    startDate?: string,
    endDate?: string
  ): Promise<ActivityCalendarResponse> {
    const params = new URLSearchParams();
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);

    const queryString = params.toString();
    const url = `${API_URL}/api/activity/calendar${queryString ? `?${queryString}` : ""}`;

    const response = await fetch(url, {
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error("Failed to fetch activity calendar data");
    }

    return response.json();
  },

  async getHeatmapData(startDate?: string, endDate?: string): Promise<ActivityHeatmapResponse> {
    const params = new URLSearchParams();
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);

    const queryString = params.toString();
    const url = `${API_URL}/api/activity/heatmap${queryString ? `?${queryString}` : ""}`;

    const response = await fetch(url, {
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error("Failed to fetch activity heatmap data");
    }

    return response.json();
  },

  async getStreakData(): Promise<StreakData> {
    const response = await fetch(`${API_URL}/api/activity/streak`, {
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error("Failed to fetch streak data");
    }

    return response.json();
  },

  async getDailyStats(targetDate?: string): Promise<DailyActivityStats> {
    const params = new URLSearchParams();
    if (targetDate) params.append("target_date", targetDate);

    const queryString = params.toString();
    const url = `${API_URL}/api/activity/daily${queryString ? `?${queryString}` : ""}`;

    const response = await fetch(url, {
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error("Failed to fetch daily activity stats");
    }

    return response.json();
  },
};
