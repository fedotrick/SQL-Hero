import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { achievementsService, AchievementsError } from "./achievements";
import type { AchievementsListResponse } from "../types/achievements";

describe("achievementsService", () => {
  const mockToken = "test-token-123";

  beforeEach(() => {
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("getAchievements", () => {
    it("should successfully fetch achievements", async () => {
      const mockResponse: AchievementsListResponse = {
        achievements: [
          {
            id: 1,
            code: "first_lesson",
            type: "lesson",
            title: "First Steps",
            description: "Complete your first lesson",
            icon: "star",
            points: 10,
            criteria: "Complete 1 lesson",
            created_at: "2024-01-01T00:00:00Z",
            is_earned: true,
            earned_at: "2024-01-02T00:00:00Z",
            progress: null,
          },
          {
            id: 2,
            code: "ten_lessons",
            type: "lesson",
            title: "Dedicated Learner",
            description: "Complete 10 lessons",
            icon: "trophy",
            points: 50,
            criteria: "Complete 10 lessons",
            created_at: "2024-01-01T00:00:00Z",
            is_earned: false,
            earned_at: null,
            progress: {
              current: 5,
              target: 10,
              percentage: 50,
            },
          },
        ],
        total_earned: 1,
        total_points: 10,
      };

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await achievementsService.getAchievements(mockToken);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/achievements"),
        expect.objectContaining({
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${mockToken}`,
          },
        })
      );

      expect(result).toEqual(mockResponse);
      expect(result.achievements).toHaveLength(2);
      expect(result.total_earned).toBe(1);
      expect(result.total_points).toBe(10);
    });

    it("should handle empty achievements list", async () => {
      const mockResponse: AchievementsListResponse = {
        achievements: [],
        total_earned: 0,
        total_points: 0,
      };

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await achievementsService.getAchievements(mockToken);

      expect(result.achievements).toHaveLength(0);
      expect(result.total_earned).toBe(0);
      expect(result.total_points).toBe(0);
    });

    it("should throw AchievementsError on 401 unauthorized", async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
        ok: false,
        status: 401,
        json: async () => ({ detail: "Unauthorized" }),
      });

      await expect(achievementsService.getAchievements(mockToken)).rejects.toThrow(
        AchievementsError
      );
      
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
        ok: false,
        status: 401,
        json: async () => ({ detail: "Unauthorized" }),
      });
      
      await expect(achievementsService.getAchievements(mockToken)).rejects.toThrow(
        "Unauthorized"
      );
    });

    it("should throw AchievementsError on 500 server error", async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: "Internal server error" }),
      });

      await expect(achievementsService.getAchievements(mockToken)).rejects.toThrow(
        AchievementsError
      );
    });

    it("should throw AchievementsError on network error", async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
        new Error("Network failure")
      );

      await expect(achievementsService.getAchievements(mockToken)).rejects.toThrow(
        AchievementsError
      );
      await expect(achievementsService.getAchievements(mockToken)).rejects.toThrow(
        /Network error/
      );
    });

    it("should correctly format achievement with progress", async () => {
      const mockResponse: AchievementsListResponse = {
        achievements: [
          {
            id: 1,
            code: "streak_7",
            type: "streak",
            title: "Week Warrior",
            description: "Maintain a 7-day streak",
            icon: "trophy",
            points: 30,
            criteria: "Complete lessons for 7 consecutive days",
            created_at: "2024-01-01T00:00:00Z",
            is_earned: false,
            earned_at: null,
            progress: {
              current: 3,
              target: 7,
              percentage: 42.857142857142854,
            },
          },
        ],
        total_earned: 0,
        total_points: 0,
      };

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await achievementsService.getAchievements(mockToken);

      expect(result.achievements[0].progress).toBeDefined();
      expect(result.achievements[0].progress?.current).toBe(3);
      expect(result.achievements[0].progress?.target).toBe(7);
      expect(result.achievements[0].progress?.percentage).toBeCloseTo(42.86, 2);
    });

    it("should handle achievements without progress", async () => {
      const mockResponse: AchievementsListResponse = {
        achievements: [
          {
            id: 1,
            code: "first_lesson",
            type: "lesson",
            title: "First Steps",
            description: "Complete your first lesson",
            icon: "star",
            points: 10,
            criteria: null,
            created_at: "2024-01-01T00:00:00Z",
            is_earned: true,
            earned_at: "2024-01-02T12:30:00Z",
            progress: null,
          },
        ],
        total_earned: 1,
        total_points: 10,
      };

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await achievementsService.getAchievements(mockToken);

      expect(result.achievements[0].is_earned).toBe(true);
      expect(result.achievements[0].earned_at).toBe("2024-01-02T12:30:00Z");
      expect(result.achievements[0].progress).toBeNull();
    });
  });
});
