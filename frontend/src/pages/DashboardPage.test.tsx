import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { renderWithProviders } from "../test/utils";
import { DashboardPage } from "./DashboardPage";
import type { UserProgressSummary, ActivityHeatmapResponse } from "../types/progress";

const mockProgressSummary: UserProgressSummary = {
  user_id: 1,
  username: "testuser",
  xp: 350,
  level: 4,
  xp_to_next_level: 50,
  current_level_xp: 300,
  next_level_xp: 400,
  progress_percentage: 50,
  current_streak: 7,
  longest_streak: 14,
  total_queries: 42,
  lessons_completed: 15,
  total_lessons: 30,
  modules_completed: 2,
  total_modules: 5,
  achievements_count: 8,
  last_active_date: "2024-01-15T10:00:00Z",
};

const mockHeatmapData: ActivityHeatmapResponse = {
  user_id: 1,
  start_date: "2023-12-01",
  end_date: "2024-01-15",
  data: [
    { date: "2024-01-01", count: 5 },
    { date: "2024-01-02", count: 3 },
    { date: "2024-01-03", count: 0 },
    { date: "2024-01-04", count: 8 },
  ],
  total_activities: 16,
};

vi.mock("../store/authStore", () => ({
  useAuthStore: () => ({
    token: "test-token",
    user: { id: 1, username: "testuser" },
  }),
}));

const mockUseProgressSummary = vi.fn();
const mockUseActivityHeatmap = vi.fn();

vi.mock("../hooks/useProgressSummary", () => ({
  useProgressSummary: () => mockUseProgressSummary(),
}));

vi.mock("../hooks/useActivityHeatmap", () => ({
  useActivityHeatmap: () => mockUseActivityHeatmap(),
}));

describe("DashboardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Loading State", () => {
    it("should show skeleton loading state when data is loading", () => {
      mockUseProgressSummary.mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
      });

      mockUseActivityHeatmap.mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
      });

      const { container } = renderWithProviders(<DashboardPage />);

      const skeletons = container.querySelectorAll('[aria-hidden="true"]');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe("Error State", () => {
    it("should show error message when progress data fails to load", async () => {
      mockUseProgressSummary.mockReturnValue({
        data: undefined,
        isLoading: false,
        error: new Error("Failed to fetch progress"),
      });

      mockUseActivityHeatmap.mockReturnValue({
        data: undefined,
        isLoading: false,
        error: null,
      });

      renderWithProviders(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText("Failed to load dashboard")).toBeInTheDocument();
        expect(screen.getByText("Failed to fetch progress")).toBeInTheDocument();
      });
    });
  });

  describe("Success State", () => {
    beforeEach(() => {
      mockUseProgressSummary.mockReturnValue({
        data: mockProgressSummary,
        isLoading: false,
        error: null,
      });

      mockUseActivityHeatmap.mockReturnValue({
        data: mockHeatmapData,
        isLoading: false,
        error: null,
      });
    });

    it("should render hero header with user info", async () => {
      renderWithProviders(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText("testuser")).toBeInTheDocument();
        expect(screen.getByText("Level 4")).toBeInTheDocument();
        expect(screen.getByText("350 XP")).toBeInTheDocument();
      });
    });

    it("should render level progress bar", async () => {
      renderWithProviders(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText("50 XP to next level")).toBeInTheDocument();
        expect(screen.getByText("Level Progress")).toBeInTheDocument();
      });
    });

    it("should render quick stats cards", async () => {
      renderWithProviders(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText("Current Streak")).toBeInTheDocument();
        expect(screen.getByText("7")).toBeInTheDocument();
        expect(screen.getByText("Best: 14")).toBeInTheDocument();

        expect(screen.getByText("Achievements")).toBeInTheDocument();
        expect(screen.getByText("8")).toBeInTheDocument();

        expect(screen.getByText("Lessons Done")).toBeInTheDocument();
        expect(screen.getByText("15/30")).toBeInTheDocument();

        expect(screen.getByText("Total Queries")).toBeInTheDocument();
        expect(screen.getByText("42")).toBeInTheDocument();
      });
    });

    it("should render module progress section", async () => {
      renderWithProviders(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText("Module Progress")).toBeInTheDocument();
        expect(screen.getByText("2 / 5")).toBeInTheDocument();
        expect(screen.getByText("15 / 30")).toBeInTheDocument();
      });
    });

    it("should render activity heatmap", async () => {
      renderWithProviders(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText("Activity Heatmap")).toBeInTheDocument();
        expect(screen.getByText("Total activities: 16")).toBeInTheDocument();
      });
    });

    it("should display last active date", async () => {
      renderWithProviders(<DashboardPage />);

      await waitFor(() => {
        const dateElement = screen.getByText(/Last active:/);
        expect(dateElement).toBeInTheDocument();
      });
    });
  });

  describe("Empty State", () => {
    it("should show empty state when no heatmap data", async () => {
      mockUseProgressSummary.mockReturnValue({
        data: mockProgressSummary,
        isLoading: false,
        error: null,
      });

      mockUseActivityHeatmap.mockReturnValue({
        data: {
          ...mockHeatmapData,
          data: [],
          total_activities: 0,
        },
        isLoading: false,
        error: null,
      });

      renderWithProviders(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByText("No activity data yet")).toBeInTheDocument();
        expect(
          screen.getByText("Start completing lessons to see your progress!")
        ).toBeInTheDocument();
      });
    });
  });

  describe("Animations", () => {
    it("should render animated components", async () => {
      mockUseProgressSummary.mockReturnValue({
        data: mockProgressSummary,
        isLoading: false,
        error: null,
      });

      mockUseActivityHeatmap.mockReturnValue({
        data: mockHeatmapData,
        isLoading: false,
        error: null,
      });

      const { container } = renderWithProviders(<DashboardPage />);

      await waitFor(() => {
        const motionElements = container.querySelectorAll("[style*='opacity']");
        expect(motionElements.length).toBeGreaterThan(0);
      });
    });
  });
});
