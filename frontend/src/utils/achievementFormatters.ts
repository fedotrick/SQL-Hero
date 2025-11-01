import type { Achievement, AchievementProgress } from "../types/achievements";

export const formatAchievementDate = (dateString: string | null): string => {
  if (!dateString) return "";

  const date = new Date(dateString);
  return date.toLocaleDateString("ru-RU", {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

export const formatProgressPercentage = (progress: AchievementProgress | null): string => {
  if (!progress) return "0%";
  return `${Math.round(progress.percentage)}%`;
};

export const formatProgressRatio = (progress: AchievementProgress | null): string => {
  if (!progress) return "0/0";
  return `${progress.current}/${progress.target}`;
};

export const getAchievementStatusText = (achievement: Achievement): string => {
  if (achievement.is_earned) {
    return "Открыто";
  }
  return "Заблокировано";
};

export const calculateCompletionPercentage = (
  earned: number,
  total: number
): number => {
  if (total === 0) return 0;
  return Math.round((earned / total) * 100);
};

export const sortAchievementsByStatus = (achievements: Achievement[]): Achievement[] => {
  return [...achievements].sort((a, b) => {
    if (a.is_earned === b.is_earned) {
      return a.id - b.id;
    }
    return a.is_earned ? -1 : 1;
  });
};

export const filterEarnedAchievements = (achievements: Achievement[]): Achievement[] => {
  return achievements.filter((a) => a.is_earned);
};

export const filterLockedAchievements = (achievements: Achievement[]): Achievement[] => {
  return achievements.filter((a) => !a.is_earned);
};

export const getAchievementsWithProgress = (achievements: Achievement[]): Achievement[] => {
  return achievements.filter((a) => !a.is_earned && a.progress !== null);
};

export const getTotalPointsEarned = (achievements: Achievement[]): number => {
  return achievements
    .filter((a) => a.is_earned)
    .reduce((sum, a) => sum + a.points, 0);
};

export const getAchievementIcon = (iconName: string | null): string => {
  const iconMap: Record<string, string> = {
    trophy: "🏆",
    star: "⭐",
    award: "🎖️",
    target: "🎯",
    medal: "🥇",
    fire: "🔥",
  };

  return iconMap[iconName || ""] || "🏆";
};
