import { useQuery } from "@tanstack/react-query";
import { progressApi } from "../services/api";
import { useAuthStore } from "../store/authStore";
import type { UserProgressSummary } from "../types/progress";

export const useProgressSummary = () => {
  const { token } = useAuthStore();

  return useQuery<UserProgressSummary>({
    queryKey: ["progress", "summary"],
    queryFn: () => {
      if (!token) {
        throw new Error("No authentication token available");
      }
      return progressApi.getSummary(token);
    },
    enabled: !!token,
    staleTime: 1000 * 60 * 2,
  });
};
