import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { render } from "../test/utils";
import { AchievementsPage } from "./AchievementsPage";
import { useAuthStore } from "../store/authStore";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import * as achievementsService from "../services/achievements";

vi.mock("../store/authStore");
vi.mock("../services/achievements");

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe("AchievementsPage", () => {
  const mockToken = "test-token-123";

  beforeEach(() => {
    vi.mocked(useAuthStore).mockReturnValue({
      token: mockToken,
      status: "authenticated",
      user: null,
      error: null,
      setLoading: vi.fn(),
      setAuthenticated: vi.fn(),
      setError: vi.fn(),
      setNotInTelegram: vi.fn(),
      logout: vi.fn(),
      initialize: vi.fn(),
    });
  });

  it("should render loading state initially", () => {
    vi.spyOn(achievementsService.achievementsService, "getAchievements").mockImplementation(
      () => new Promise(() => {})
    );

    render(<AchievementsPage />, { wrapper: createWrapper() });

    expect(screen.getByText(/authenticating/i)).toBeInTheDocument();
  });

  it("should render achievements list with correct data", async () => {
    const mockData = {
      achievements: [
        {
          id: 1,
          code: "first_lesson",
          type: "lesson",
          title: "Первые шаги",
          description: "Завершите первый урок",
          icon: "star",
          points: 10,
          criteria: "Завершить 1 урок",
          created_at: "2024-01-01T00:00:00Z",
          is_earned: true,
          earned_at: "2024-01-02T00:00:00Z",
          progress: null,
        },
        {
          id: 2,
          code: "ten_lessons",
          type: "lesson",
          title: "Преданный ученик",
          description: "Завершите 10 уроков",
          icon: "trophy",
          points: 50,
          criteria: "Завершить 10 уроков",
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

    vi.spyOn(achievementsService.achievementsService, "getAchievements").mockResolvedValue(
      mockData
    );

    render(<AchievementsPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText("Достижения")).toBeInTheDocument();
    });

    expect(screen.getByText("Первые шаги")).toBeInTheDocument();
    expect(screen.getByText("Преданный ученик")).toBeInTheDocument();
    expect(screen.getByText("Завершите первый урок")).toBeInTheDocument();
    expect(screen.getByText("Завершите 10 уроков")).toBeInTheDocument();
  });

  it("should display correct statistics", async () => {
    const mockData = {
      achievements: [
        {
          id: 1,
          code: "first_lesson",
          type: "lesson",
          title: "First Steps",
          description: "Complete first lesson",
          icon: "star",
          points: 10,
          criteria: null,
          created_at: "2024-01-01T00:00:00Z",
          is_earned: true,
          earned_at: "2024-01-02T00:00:00Z",
          progress: null,
        },
        {
          id: 2,
          code: "second_achievement",
          type: "lesson",
          title: "Second Achievement",
          description: "Second achievement",
          icon: "trophy",
          points: 20,
          criteria: null,
          created_at: "2024-01-01T00:00:00Z",
          is_earned: false,
          earned_at: null,
          progress: null,
        },
      ],
      total_earned: 1,
      total_points: 10,
    };

    vi.spyOn(achievementsService.achievementsService, "getAchievements").mockResolvedValue(
      mockData
    );

    render(<AchievementsPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText("1/2")).toBeInTheDocument();
    });

    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByText("50%")).toBeInTheDocument();
  });

  it("should show progress bar for locked achievements", async () => {
    const mockData = {
      achievements: [
        {
          id: 1,
          code: "ten_lessons",
          type: "lesson",
          title: "Ten Lessons",
          description: "Complete 10 lessons",
          icon: "trophy",
          points: 50,
          criteria: "Complete 10 lessons",
          created_at: "2024-01-01T00:00:00Z",
          is_earned: false,
          earned_at: null,
          progress: {
            current: 7,
            target: 10,
            percentage: 70,
          },
        },
      ],
      total_earned: 0,
      total_points: 0,
    };

    vi.spyOn(achievementsService.achievementsService, "getAchievements").mockResolvedValue(
      mockData
    );

    render(<AchievementsPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText("Ten Lessons")).toBeInTheDocument();
    });

    expect(screen.getByText("7 / 10")).toBeInTheDocument();
  });

  it("should not show progress bar for earned achievements", async () => {
    const mockData = {
      achievements: [
        {
          id: 1,
          code: "first_lesson",
          type: "lesson",
          title: "Earned Achievement",
          description: "This is earned",
          icon: "star",
          points: 10,
          criteria: null,
          created_at: "2024-01-01T00:00:00Z",
          is_earned: true,
          earned_at: "2024-01-02T00:00:00Z",
          progress: null,
        },
      ],
      total_earned: 1,
      total_points: 10,
    };

    vi.spyOn(achievementsService.achievementsService, "getAchievements").mockResolvedValue(
      mockData
    );

    render(<AchievementsPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText("Earned Achievement")).toBeInTheDocument();
    });

    expect(screen.getAllByText("Открыто").length).toBeGreaterThan(0);
  });

  it("should display error screen on fetch failure", async () => {
    vi.spyOn(achievementsService.achievementsService, "getAchievements").mockRejectedValue(
      new Error("Failed to fetch")
    );

    render(<AchievementsPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText("Не удалось загрузить достижения")).toBeInTheDocument();
    });
  });

  it("should handle empty achievements list", async () => {
    const mockData = {
      achievements: [],
      total_earned: 0,
      total_points: 0,
    };

    vi.spyOn(achievementsService.achievementsService, "getAchievements").mockResolvedValue(
      mockData
    );

    render(<AchievementsPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText("Достижения пока не доступны")).toBeInTheDocument();
    });

    expect(screen.getByText("0/0")).toBeInTheDocument();
    expect(screen.getByText("0")).toBeInTheDocument();
  });

  it("should calculate completion percentage correctly", async () => {
    const mockData = {
      achievements: [
        {
          id: 1,
          code: "first",
          type: "lesson",
          title: "First",
          description: "First achievement",
          icon: "star",
          points: 10,
          criteria: null,
          created_at: "2024-01-01T00:00:00Z",
          is_earned: true,
          earned_at: "2024-01-02T00:00:00Z",
          progress: null,
        },
        {
          id: 2,
          code: "second",
          type: "lesson",
          title: "Second",
          description: "Second achievement",
          icon: "trophy",
          points: 20,
          criteria: null,
          created_at: "2024-01-01T00:00:00Z",
          is_earned: true,
          earned_at: "2024-01-02T00:00:00Z",
          progress: null,
        },
        {
          id: 3,
          code: "third",
          type: "lesson",
          title: "Third",
          description: "Third achievement",
          icon: "award",
          points: 30,
          criteria: null,
          created_at: "2024-01-01T00:00:00Z",
          is_earned: false,
          earned_at: null,
          progress: null,
        },
        {
          id: 4,
          code: "fourth",
          type: "lesson",
          title: "Fourth",
          description: "Fourth achievement",
          icon: "target",
          points: 40,
          criteria: null,
          created_at: "2024-01-01T00:00:00Z",
          is_earned: false,
          earned_at: null,
          progress: null,
        },
      ],
      total_earned: 2,
      total_points: 30,
    };

    vi.spyOn(achievementsService.achievementsService, "getAchievements").mockResolvedValue(
      mockData
    );

    render(<AchievementsPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText("2/4")).toBeInTheDocument();
    });

    expect(screen.getByText("50%")).toBeInTheDocument();
  });
});
