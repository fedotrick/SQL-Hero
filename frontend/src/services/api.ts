import type { UserProgressSummary, ActivityHeatmapResponse } from "../types/progress";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

class ApiError extends Error {
  statusCode: number;

  constructor(message: string, statusCode: number) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
  }
}

async function fetchWithAuth<T>(endpoint: string, token: string): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({
      detail: "Request failed",
    }));
    throw new ApiError(
      errorData.detail || `Request failed with status ${response.status}`,
      response.status
    );
  }

  return response.json();
}

export const progressApi = {
  getSummary: (token: string): Promise<UserProgressSummary> => {
    return fetchWithAuth<UserProgressSummary>("/progress/summary", token);
  },
};

export const activityApi = {
  getHeatmap: (
    token: string,
    startDate?: string,
    endDate?: string
  ): Promise<ActivityHeatmapResponse> => {
    const params = new URLSearchParams();
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);
    const query = params.toString() ? `?${params.toString()}` : "";
    return fetchWithAuth<ActivityHeatmapResponse>(`/activity/heatmap${query}`, token);
  },
};
