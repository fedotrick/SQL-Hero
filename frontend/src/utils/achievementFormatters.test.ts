import { describe, it, expect } from "vitest";
import type { Achievement } from "../types/achievements";
import {
  formatAchievementDate,
  formatProgressPercentage,
  formatProgressRatio,
  getAchievementStatusText,
  calculateCompletionPercentage,
  sortAchievementsByStatus,
  filterEarnedAchievements,
  filterLockedAchievements,
  getAchievementsWithProgress,
  getTotalPointsEarned,
  getAchievementIcon,
} from "./achievementFormatters";

describe("achievementFormatters", () => {
  const createMockAchievement = (overrides: Partial<Achievement> = {}): Achievement => ({
    id: 1,
    code: "test_achievement",
    type: "lesson",
    title: "Test Achievement",
    description: "Test description",
    icon: "trophy",
    points: 10,
    criteria: "Test criteria",
    created_at: "2024-01-01T00:00:00Z",
    is_earned: false,
    earned_at: null,
    progress: null,
    ...overrides,
  });

  describe("formatAchievementDate", () => {
    it("should format date string correctly", () => {
      const dateString = "2024-01-15T14:30:00Z";
      const result = formatAchievementDate(dateString);
      expect(result).toContain("2024");
    });

    it("should return empty string for null date", () => {
      const result = formatAchievementDate(null);
      expect(result).toBe("");
    });
  });

  describe("formatProgressPercentage", () => {
    it("should format progress percentage correctly", () => {
      const progress = { current: 5, target: 10, percentage: 50 };
      const result = formatProgressPercentage(progress);
      expect(result).toBe("50%");
    });

    it("should round percentage to nearest integer", () => {
      const progress = { current: 1, target: 3, percentage: 33.333333 };
      const result = formatProgressPercentage(progress);
      expect(result).toBe("33%");
    });

    it("should return 0% for null progress", () => {
      const result = formatProgressPercentage(null);
      expect(result).toBe("0%");
    });
  });

  describe("formatProgressRatio", () => {
    it("should format progress ratio correctly", () => {
      const progress = { current: 5, target: 10, percentage: 50 };
      const result = formatProgressRatio(progress);
      expect(result).toBe("5/10");
    });

    it("should return 0/0 for null progress", () => {
      const result = formatProgressRatio(null);
      expect(result).toBe("0/0");
    });
  });

  describe("getAchievementStatusText", () => {
    it("should return Открыто for earned achievement", () => {
      const achievement = createMockAchievement({ is_earned: true });
      const result = getAchievementStatusText(achievement);
      expect(result).toBe("Открыто");
    });

    it("should return Заблокировано for locked achievement", () => {
      const achievement = createMockAchievement({ is_earned: false });
      const result = getAchievementStatusText(achievement);
      expect(result).toBe("Заблокировано");
    });
  });

  describe("calculateCompletionPercentage", () => {
    it("should calculate completion percentage correctly", () => {
      expect(calculateCompletionPercentage(3, 10)).toBe(30);
      expect(calculateCompletionPercentage(5, 10)).toBe(50);
      expect(calculateCompletionPercentage(10, 10)).toBe(100);
    });

    it("should round to nearest integer", () => {
      expect(calculateCompletionPercentage(1, 3)).toBe(33);
      expect(calculateCompletionPercentage(2, 3)).toBe(67);
    });

    it("should return 0 for zero total", () => {
      expect(calculateCompletionPercentage(5, 0)).toBe(0);
    });

    it("should return 0 for zero earned", () => {
      expect(calculateCompletionPercentage(0, 10)).toBe(0);
    });
  });

  describe("sortAchievementsByStatus", () => {
    it("should sort earned achievements before locked ones", () => {
      const achievements = [
        createMockAchievement({ id: 1, is_earned: false }),
        createMockAchievement({ id: 2, is_earned: true }),
        createMockAchievement({ id: 3, is_earned: false }),
        createMockAchievement({ id: 4, is_earned: true }),
      ];

      const sorted = sortAchievementsByStatus(achievements);

      expect(sorted[0].id).toBe(2);
      expect(sorted[1].id).toBe(4);
      expect(sorted[2].id).toBe(1);
      expect(sorted[3].id).toBe(3);
    });

    it("should maintain order by id for same status", () => {
      const achievements = [
        createMockAchievement({ id: 3, is_earned: true }),
        createMockAchievement({ id: 1, is_earned: true }),
        createMockAchievement({ id: 2, is_earned: true }),
      ];

      const sorted = sortAchievementsByStatus(achievements);

      expect(sorted[0].id).toBe(1);
      expect(sorted[1].id).toBe(2);
      expect(sorted[2].id).toBe(3);
    });
  });

  describe("filterEarnedAchievements", () => {
    it("should return only earned achievements", () => {
      const achievements = [
        createMockAchievement({ id: 1, is_earned: true }),
        createMockAchievement({ id: 2, is_earned: false }),
        createMockAchievement({ id: 3, is_earned: true }),
      ];

      const filtered = filterEarnedAchievements(achievements);

      expect(filtered).toHaveLength(2);
      expect(filtered[0].id).toBe(1);
      expect(filtered[1].id).toBe(3);
    });

    it("should return empty array when no achievements are earned", () => {
      const achievements = [
        createMockAchievement({ id: 1, is_earned: false }),
        createMockAchievement({ id: 2, is_earned: false }),
      ];

      const filtered = filterEarnedAchievements(achievements);

      expect(filtered).toHaveLength(0);
    });
  });

  describe("filterLockedAchievements", () => {
    it("should return only locked achievements", () => {
      const achievements = [
        createMockAchievement({ id: 1, is_earned: true }),
        createMockAchievement({ id: 2, is_earned: false }),
        createMockAchievement({ id: 3, is_earned: false }),
      ];

      const filtered = filterLockedAchievements(achievements);

      expect(filtered).toHaveLength(2);
      expect(filtered[0].id).toBe(2);
      expect(filtered[1].id).toBe(3);
    });
  });

  describe("getAchievementsWithProgress", () => {
    it("should return only locked achievements with progress", () => {
      const achievements = [
        createMockAchievement({ id: 1, is_earned: true, progress: null }),
        createMockAchievement({
          id: 2,
          is_earned: false,
          progress: { current: 5, target: 10, percentage: 50 },
        }),
        createMockAchievement({ id: 3, is_earned: false, progress: null }),
        createMockAchievement({
          id: 4,
          is_earned: false,
          progress: { current: 2, target: 5, percentage: 40 },
        }),
      ];

      const filtered = getAchievementsWithProgress(achievements);

      expect(filtered).toHaveLength(2);
      expect(filtered[0].id).toBe(2);
      expect(filtered[1].id).toBe(4);
    });
  });

  describe("getTotalPointsEarned", () => {
    it("should calculate total points from earned achievements", () => {
      const achievements = [
        createMockAchievement({ id: 1, is_earned: true, points: 10 }),
        createMockAchievement({ id: 2, is_earned: false, points: 20 }),
        createMockAchievement({ id: 3, is_earned: true, points: 30 }),
        createMockAchievement({ id: 4, is_earned: true, points: 15 }),
      ];

      const total = getTotalPointsEarned(achievements);

      expect(total).toBe(55);
    });

    it("should return 0 when no achievements are earned", () => {
      const achievements = [
        createMockAchievement({ id: 1, is_earned: false, points: 10 }),
        createMockAchievement({ id: 2, is_earned: false, points: 20 }),
      ];

      const total = getTotalPointsEarned(achievements);

      expect(total).toBe(0);
    });

    it("should return 0 for empty array", () => {
      const total = getTotalPointsEarned([]);
      expect(total).toBe(0);
    });
  });

  describe("getAchievementIcon", () => {
    it("should return correct emoji for known icon names", () => {
      expect(getAchievementIcon("trophy")).toBe("🏆");
      expect(getAchievementIcon("star")).toBe("⭐");
      expect(getAchievementIcon("award")).toBe("🎖️");
      expect(getAchievementIcon("target")).toBe("🎯");
      expect(getAchievementIcon("medal")).toBe("🥇");
      expect(getAchievementIcon("fire")).toBe("🔥");
    });

    it("should return default trophy emoji for unknown icon names", () => {
      expect(getAchievementIcon("unknown")).toBe("🏆");
    });

    it("should return default trophy emoji for null", () => {
      expect(getAchievementIcon(null)).toBe("🏆");
    });
  });
});
