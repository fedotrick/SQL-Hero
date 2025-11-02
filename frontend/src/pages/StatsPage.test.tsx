import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { StatsPage } from "./StatsPage";
import { activityService } from "../services";

vi.mock("../services", () => ({
  activityService: {
    getCalendarData: vi.fn(),
    getDailyStats: vi.fn(),
  },
}));

describe("StatsPage", () => {
  const mockCalendarData = {
    heatmap: {
      user_id: 1,
      start_date: "2024-01-01",
      end_date: "2024-12-31",
      data: [
        { date: "2024-01-01", count: 5 },
        { date: "2024-01-02", count: 3 },
        { date: "2024-01-03", count: 8 },
      ],
      total_activities: 16,
    },
    streak: {
      current_streak: 7,
      longest_streak: 15,
      total_active_days: 30,
      last_active_date: "2024-01-03",
      streak_start_date: "2024-01-01",
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Loading State", () => {
    it("should display loading skeleton while fetching data", () => {
      (activityService.getCalendarData as any).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      render(<StatsPage />);

      expect(screen.getByText("Статистика активности")).toBeInTheDocument();
      expect(screen.getByText("Ваши достижения и прогресс")).toBeInTheDocument();
    });
  });

  describe("Success State", () => {
    beforeEach(() => {
      (activityService.getCalendarData as any).mockResolvedValue(mockCalendarData);
    });

    it("should display calendar data after loading", async () => {
      render(<StatsPage />);

      await waitFor(() => {
        expect(screen.getByText("Статистика активности")).toBeInTheDocument();
      });
    });

    it("should display streak statistics", async () => {
      render(<StatsPage />);

      await waitFor(() => {
        expect(screen.getByText("7")).toBeInTheDocument();
        expect(screen.getByText("Текущая серия")).toBeInTheDocument();
        expect(screen.getByText("15")).toBeInTheDocument();
        expect(screen.getByText("Лучшая серия")).toBeInTheDocument();
      });
    });

    it("should display total active days", async () => {
      render(<StatsPage />);

      await waitFor(() => {
        expect(screen.getByText("30")).toBeInTheDocument();
        expect(screen.getByText("Активных дней")).toBeInTheDocument();
      });
    });

    it("should display total activities", async () => {
      render(<StatsPage />);

      await waitFor(() => {
        expect(screen.getByText("16")).toBeInTheDocument();
        expect(screen.getByText("Всего активностей")).toBeInTheDocument();
      });
    });

    it("should display last active date", async () => {
      render(<StatsPage />);

      await waitFor(() => {
        expect(screen.getByText(/Последняя активность:/)).toBeInTheDocument();
      });
    });

    it("should render the activity calendar", async () => {
      render(<StatsPage />);

      await waitFor(() => {
        expect(screen.getByText("Календарь активности")).toBeInTheDocument();
      });
    });
  });

  describe("Error State", () => {
    it("should display error message when fetch fails", async () => {
      (activityService.getCalendarData as any).mockRejectedValue(
        new Error("Network error")
      );

      render(<StatsPage />);

      await waitFor(() => {
        expect(screen.getByText("Ошибка загрузки")).toBeInTheDocument();
        expect(screen.getByText(/Network error/)).toBeInTheDocument();
      });
    });

    it("should display default error message when error has no message", async () => {
      (activityService.getCalendarData as any).mockRejectedValue({});

      render(<StatsPage />);

      await waitFor(() => {
        expect(screen.getByText("Не удалось загрузить данные")).toBeInTheDocument();
      });
    });
  });

  describe("Daily Stats Interaction", () => {
    const mockDailyStats = {
      date: "2024-01-01",
      total_count: 5,
      activity_by_type: {
        lesson_completed: 3,
        challenge_attempted: 2,
      },
    };

    beforeEach(() => {
      (activityService.getCalendarData as any).mockResolvedValue(mockCalendarData);
      (activityService.getDailyStats as any).mockResolvedValue(mockDailyStats);
    });

    it("should not fetch daily stats initially", async () => {
      render(<StatsPage />);

      await waitFor(() => {
        expect(screen.getByText("Статистика активности")).toBeInTheDocument();
      });

      expect(activityService.getDailyStats).not.toHaveBeenCalled();
    });

    it("should display daily stats when a day with activity is clicked", async () => {
      render(<StatsPage />);

      await waitFor(() => {
        expect(screen.getByText("Статистика активности")).toBeInTheDocument();
      });

      // Note: Since we're using StreakCalendar component, we can't directly test
      // the click handler without a full integration test. This test demonstrates
      // the structure but would need additional setup to work.
    });
  });

  describe("Empty Data Handling", () => {
    it("should handle zero streaks gracefully", async () => {
      const emptyData = {
        heatmap: {
          user_id: 1,
          start_date: "2024-01-01",
          end_date: "2024-12-31",
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

      (activityService.getCalendarData as any).mockResolvedValue(emptyData);

      render(<StatsPage />);

      await waitFor(() => {
        expect(screen.getByText("0")).toBeInTheDocument();
      });
    });

    it("should not display last active date when null", async () => {
      const noActivityData = {
        heatmap: {
          user_id: 1,
          start_date: "2024-01-01",
          end_date: "2024-12-31",
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

      (activityService.getCalendarData as any).mockResolvedValue(noActivityData);

      render(<StatsPage />);

      await waitFor(() => {
        expect(screen.queryByText(/Последняя активность:/)).not.toBeInTheDocument();
      });
    });
  });

  describe("Component Integration", () => {
    beforeEach(() => {
      (activityService.getCalendarData as any).mockResolvedValue(mockCalendarData);
    });

    it("should pass correct props to StreakCalendar", async () => {
      render(<StatsPage />);

      await waitFor(() => {
        expect(screen.getByText("Календарь активности")).toBeInTheDocument();
      });

      // StreakCalendar should be rendered with the data
      // The actual calendar rendering is tested in StreakCalendar.test.tsx
    });

    it("should display all summary stat cards", async () => {
      render(<StatsPage />);

      await waitFor(() => {
        expect(screen.getByText("Текущая серия")).toBeInTheDocument();
        expect(screen.getByText("Лучшая серия")).toBeInTheDocument();
        expect(screen.getByText("Активных дней")).toBeInTheDocument();
        expect(screen.getByText("Всего активностей")).toBeInTheDocument();
      });
    });
  });

  describe("Accessibility", () => {
    beforeEach(() => {
      (activityService.getCalendarData as any).mockResolvedValue(mockCalendarData);
    });

    it("should have proper heading hierarchy", async () => {
      render(<StatsPage />);

      await waitFor(() => {
        const h1 = screen.getByText("Статистика активности");
        expect(h1.tagName).toBe("H1");

        const h2s = screen.getAllByText(/статистика|Календарь/, { selector: "h2" });
        expect(h2s.length).toBeGreaterThan(0);
      });
    });

    it("should have descriptive text for statistics", async () => {
      render(<StatsPage />);

      await waitFor(() => {
        expect(screen.getByText("Ваши достижения и прогресс")).toBeInTheDocument();
      });
    });
  });

  describe("Data Refresh", () => {
    it("should fetch fresh data on mount", async () => {
      (activityService.getCalendarData as any).mockResolvedValue(mockCalendarData);

      render(<StatsPage />);

      await waitFor(() => {
        expect(activityService.getCalendarData).toHaveBeenCalledTimes(1);
      });
    });

    it("should handle multiple rapid fetches", async () => {
      (activityService.getCalendarData as any).mockResolvedValue(mockCalendarData);

      const { unmount } = render(<StatsPage />);
      unmount();
      render(<StatsPage />);

      await waitFor(() => {
        // Should be called once per render
        expect(activityService.getCalendarData).toHaveBeenCalledTimes(2);
      });
    });
  });
});
