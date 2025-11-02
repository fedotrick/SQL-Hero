import { describe, it, expect, vi, beforeEach } from "vitest";
import { activityService } from "./activity";

// Mock fetch globally
global.fetch = vi.fn();

describe("activityService", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getCalendarData", () => {
    it("should fetch calendar data without parameters", async () => {
      const mockResponse = {
        heatmap: {
          user_id: 1,
          start_date: "2024-01-01",
          end_date: "2024-12-31",
          data: [
            { date: "2024-01-01", count: 5 },
            { date: "2024-01-02", count: 3 },
          ],
          total_activities: 8,
        },
        streak: {
          current_streak: 5,
          longest_streak: 10,
          total_active_days: 20,
          last_active_date: "2024-01-02",
          streak_start_date: "2024-01-01",
        },
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await activityService.getCalendarData();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/activity/calendar"),
        expect.objectContaining({ credentials: "include" })
      );
      expect(result).toEqual(mockResponse);
    });

    it("should fetch calendar data with date range", async () => {
      const mockResponse = {
        heatmap: {
          user_id: 1,
          start_date: "2024-01-01",
          end_date: "2024-01-31",
          data: [],
          total_activities: 0,
        },
        streak: {
          current_streak: 0,
          longest_streak: 0,
          total_active_days: 0,
          last_active_date: null,
          streak_start_date: null,
        },
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await activityService.getCalendarData("2024-01-01", "2024-01-31");

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("start_date=2024-01-01"),
        expect.anything()
      );
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("end_date=2024-01-31"),
        expect.anything()
      );
      expect(result).toEqual(mockResponse);
    });

    it("should throw error when request fails", async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      await expect(activityService.getCalendarData()).rejects.toThrow(
        "Failed to fetch activity calendar data"
      );
    });
  });

  describe("getHeatmapData", () => {
    it("should fetch heatmap data", async () => {
      const mockResponse = {
        user_id: 1,
        start_date: "2024-01-01",
        end_date: "2024-12-31",
        data: [
          { date: "2024-01-01", count: 5 },
          { date: "2024-01-02", count: 3 },
        ],
        total_activities: 8,
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await activityService.getHeatmapData();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/activity/heatmap"),
        expect.objectContaining({ credentials: "include" })
      );
      expect(result).toEqual(mockResponse);
    });

    it("should handle date parameters", async () => {
      const mockResponse = {
        user_id: 1,
        start_date: "2024-06-01",
        end_date: "2024-06-30",
        data: [],
        total_activities: 0,
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      await activityService.getHeatmapData("2024-06-01", "2024-06-30");

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("start_date=2024-06-01"),
        expect.anything()
      );
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("end_date=2024-06-30"),
        expect.anything()
      );
    });

    it("should throw error on failure", async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      await expect(activityService.getHeatmapData()).rejects.toThrow(
        "Failed to fetch activity heatmap data"
      );
    });
  });

  describe("getStreakData", () => {
    it("should fetch streak data", async () => {
      const mockResponse = {
        current_streak: 7,
        longest_streak: 15,
        total_active_days: 30,
        last_active_date: "2024-01-15",
        streak_start_date: "2024-01-09",
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await activityService.getStreakData();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/activity/streak"),
        expect.objectContaining({ credentials: "include" })
      );
      expect(result).toEqual(mockResponse);
    });

    it("should handle zero streaks", async () => {
      const mockResponse = {
        current_streak: 0,
        longest_streak: 0,
        total_active_days: 0,
        last_active_date: null,
        streak_start_date: null,
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await activityService.getStreakData();
      expect(result.current_streak).toBe(0);
      expect(result.last_active_date).toBeNull();
    });

    it("should throw error on failure", async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      await expect(activityService.getStreakData()).rejects.toThrow(
        "Failed to fetch streak data"
      );
    });
  });

  describe("getDailyStats", () => {
    it("should fetch daily stats without date", async () => {
      const mockResponse = {
        date: "2024-01-15",
        total_count: 10,
        activity_by_type: {
          lesson_completed: 5,
          challenge_attempted: 3,
          achievement_unlocked: 2,
        },
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await activityService.getDailyStats();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/activity/daily"),
        expect.objectContaining({ credentials: "include" })
      );
      expect(result).toEqual(mockResponse);
    });

    it("should fetch daily stats with specific date", async () => {
      const mockResponse = {
        date: "2024-03-20",
        total_count: 5,
        activity_by_type: {
          lesson_completed: 5,
        },
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      await activityService.getDailyStats("2024-03-20");

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("target_date=2024-03-20"),
        expect.anything()
      );
    });

    it("should handle days with no activity", async () => {
      const mockResponse = {
        date: "2024-01-01",
        total_count: 0,
        activity_by_type: {},
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await activityService.getDailyStats("2024-01-01");
      expect(result.total_count).toBe(0);
      expect(Object.keys(result.activity_by_type)).toHaveLength(0);
    });

    it("should throw error on failure", async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      await expect(activityService.getDailyStats()).rejects.toThrow(
        "Failed to fetch daily activity stats"
      );
    });
  });

  describe("API URL construction", () => {
    it("should use environment variable for API URL", async () => {
      const mockResponse = { streak: {}, heatmap: {} };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      await activityService.getCalendarData();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringMatching(/^http:\/\/localhost:8000\/api\/activity\/calendar/),
        expect.anything()
      );
    });

    it("should properly encode query parameters", async () => {
      const mockResponse = { user_id: 1, data: [], total_activities: 0 };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      await activityService.getHeatmapData("2024-01-01", "2024-12-31");

      const [[url]] = (global.fetch as any).mock.calls;
      expect(url).toContain("start_date=2024-01-01");
      expect(url).toContain("end_date=2024-12-31");
    });
  });

  describe("Authentication", () => {
    it("should include credentials in all requests", async () => {
      const mockResponse = {};

      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });

      await activityService.getCalendarData();
      await activityService.getHeatmapData();
      await activityService.getStreakData();
      await activityService.getDailyStats();

      expect(global.fetch).toHaveBeenCalledTimes(4);
      (global.fetch as any).mock.calls.forEach(([, options]: any) => {
        expect(options.credentials).toBe("include");
      });
    });
  });
});
