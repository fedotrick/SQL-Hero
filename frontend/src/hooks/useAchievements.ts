import { useQuery } from "@tanstack/react-query";
import { useState, useEffect, useRef } from "react";
import { achievementsService } from "../services/achievements";
import type { AchievementUnlocked } from "../types/achievements";

interface UseAchievementsOptions {
  token: string | null;
  pollingInterval?: number;
  onNewAchievement?: (achievement: AchievementUnlocked) => void;
}

export const useAchievements = ({
  token,
  pollingInterval = 10000,
  onNewAchievement,
}: UseAchievementsOptions) => {
  const [newlyUnlocked, setNewlyUnlocked] = useState<AchievementUnlocked[]>([]);
  const previousEarnedIds = useRef<Set<number>>(new Set());

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["achievements", token],
    queryFn: () => {
      if (!token) throw new Error("No token available");
      return achievementsService.getAchievements(token);
    },
    enabled: !!token,
    refetchInterval: pollingInterval,
    staleTime: 5000,
  });

  useEffect(() => {
    if (data?.achievements) {
      const currentEarnedIds = new Set(
        data.achievements.filter((a) => a.is_earned).map((a) => a.id)
      );

      if (previousEarnedIds.current.size > 0) {
        const newlyEarnedIds = [...currentEarnedIds].filter(
          (id) => !previousEarnedIds.current.has(id)
        );

        if (newlyEarnedIds.length > 0) {
          const newAchievements = data.achievements
            .filter((a) => newlyEarnedIds.includes(a.id))
            .map((a) => ({
              achievement_id: a.id,
              achievement_code: a.code,
              title: a.title,
              description: a.description,
              icon: a.icon,
              points: a.points,
            }));

          newAchievements.forEach((achievement) => {
            setNewlyUnlocked((prev) => [...prev, achievement]);
            if (onNewAchievement) {
              onNewAchievement(achievement);
            }
          });
        }
      }

      previousEarnedIds.current = currentEarnedIds;
    }
  }, [data, onNewAchievement]);

  const dismissNewAchievement = (achievementId: number) => {
    setNewlyUnlocked((prev) => prev.filter((a) => a.achievement_id !== achievementId));
  };

  return {
    achievements: data?.achievements || [],
    totalEarned: data?.total_earned || 0,
    totalPoints: data?.total_points || 0,
    isLoading,
    error,
    refetch,
    newlyUnlocked,
    dismissNewAchievement,
  };
};
