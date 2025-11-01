import { useQuery } from "@tanstack/react-query";
import { activityApi } from "../services/api";
import { useAuthStore } from "../store/authStore";
import type { ActivityHeatmapResponse } from "../types/progress";

interface UseActivityHeatmapOptions {
  startDate?: string;
  endDate?: string;
}

export const useActivityHeatmap = (options?: UseActivityHeatmapOptions) => {
  const { token } = useAuthStore();

  return useQuery<ActivityHeatmapResponse>({
    queryKey: ["activity", "heatmap", options?.startDate, options?.endDate],
    queryFn: () => {
      if (!token) {
        throw new Error("No authentication token available");
      }
      return activityApi.getHeatmap(token, options?.startDate, options?.endDate);
    },
    enabled: !!token,
    staleTime: 1000 * 60 * 5,
  });
};
