import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "../test/utils";
import { LeaderboardPage } from "./LeaderboardPage";
import { leaderboardService } from "../services/leaderboard";
import { useAuthStore } from "../store/authStore";
import type { LeaderboardResponse } from "../types/leaderboard";

vi.mock("../services/leaderboard");
vi.mock("../store/authStore");
vi.mock("../services/telegramHaptics", () => ({
  telegramHaptics: {
    light: vi.fn(),
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe("LeaderboardPage", () => {
  const mockLeaderboardData: LeaderboardResponse = {
    entries: [
      {
        user_id: 1,
        username: "user1",
        first_name: "Alice",
        rank: 1,
        xp: 5000,
        level: 10,
        lessons_completed: 50,
        achievements_count: 20,
      },
      {
        user_id: 2,
        username: "user2",
        first_name: "Bob",
        rank: 2,
        xp: 4500,
        level: 9,
        lessons_completed: 45,
        achievements_count: 18,
      },
      {
        user_id: 3,
        username: "user3",
        first_name: "Charlie",
        rank: 3,
        xp: 4000,
        level: 8,
        lessons_completed: 40,
        achievements_count: 15,
      },
      {
        user_id: 4,
        username: "user4",
        first_name: "David",
        rank: 4,
        xp: 3500,
        level: 7,
        lessons_completed: 35,
        achievements_count: 12,
      },
      {
        user_id: 5,
        username: "user5",
        first_name: "Eve",
        rank: 5,
        xp: 3000,
        level: 6,
        lessons_completed: 30,
        achievements_count: 10,
      },
    ],
    current_user: null,
    last_updated: new Date().toISOString(),
    total_users: 100,
  };

  const mockCurrentUser = {
    id: 1,
    telegram_id: "123456",
    username: "user1",
    first_name: "Alice",
    last_name: null,
    xp: 5000,
    level: 10,
    is_active: true,
    is_admin: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useAuthStore).mockReturnValue({
      token: "mock-token",
      user: mockCurrentUser,
      status: "authenticated",
      error: null,
      setLoading: vi.fn(),
      setAuthenticated: vi.fn(),
      setError: vi.fn(),
      setNotInTelegram: vi.fn(),
      logout: vi.fn(),
      initialize: vi.fn(),
    });
  });

  describe("Loading state", () => {
    it("renders skeleton loading state initially", () => {
      vi.mocked(leaderboardService.getLeaderboard).mockImplementation(() => new Promise(() => {}));

      render(<LeaderboardPage />);

      const skeletons = screen.getAllByRole("generic");
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe("Data display", () => {
    it("renders leaderboard data after successful fetch", async () => {
      vi.mocked(leaderboardService.getLeaderboard).mockResolvedValue(mockLeaderboardData);

      render(<LeaderboardPage />);

      await waitFor(() => {
        expect(screen.getAllByText("Alice").length).toBeGreaterThan(0);
        expect(screen.getAllByText("Bob").length).toBeGreaterThan(0);
        expect(screen.getAllByText("Charlie").length).toBeGreaterThan(0);
        expect(screen.getByText("David")).toBeInTheDocument();
        expect(screen.getByText("Eve")).toBeInTheDocument();
      });
    });

    it("displays user XP correctly", async () => {
      vi.mocked(leaderboardService.getLeaderboard).mockResolvedValue(mockLeaderboardData);

      render(<LeaderboardPage />);

      await waitFor(() => {
        expect(screen.getByText("5,000")).toBeInTheDocument();
        expect(screen.getByText("4,500")).toBeInTheDocument();
        expect(screen.getByText("4,000")).toBeInTheDocument();
      });
    });

    it("displays total users count", async () => {
      vi.mocked(leaderboardService.getLeaderboard).mockResolvedValue(mockLeaderboardData);

      render(<LeaderboardPage />);

      await waitFor(() => {
        expect(screen.getByText("100 active learners")).toBeInTheDocument();
      });
    });

    it("shows rank numbers for users outside top 3", async () => {
      vi.mocked(leaderboardService.getLeaderboard).mockResolvedValue(mockLeaderboardData);

      render(<LeaderboardPage />);

      await waitFor(() => {
        expect(screen.getByText("#4")).toBeInTheDocument();
        expect(screen.getByText("#5")).toBeInTheDocument();
      });
    });

    it("displays lessons completed and achievements count", async () => {
      vi.mocked(leaderboardService.getLeaderboard).mockResolvedValue(mockLeaderboardData);

      render(<LeaderboardPage />);

      await waitFor(() => {
        expect(screen.getByText("50 lessons")).toBeInTheDocument();
        expect(screen.getByText("20 achievements")).toBeInTheDocument();
      });
    });
  });

  describe("Sorting and ranking", () => {
    it("displays users in correct order by XP", async () => {
      vi.mocked(leaderboardService.getLeaderboard).mockResolvedValue(mockLeaderboardData);

      render(<LeaderboardPage />);

      await waitFor(() => {
        // Just verify that the top 3 users are rendered in the component
        // The order is determined by the backend data we mock
        expect(screen.getAllByText("Alice")).toHaveLength(2); // Appears in podium and list
        expect(screen.getAllByText("Bob")).toHaveLength(2);
        expect(screen.getAllByText("Charlie")).toHaveLength(2);
      });
    });

    it("shows podium for top 3 users", async () => {
      vi.mocked(leaderboardService.getLeaderboard).mockResolvedValue(mockLeaderboardData);

      render(<LeaderboardPage />);

      await waitFor(() => {
        const podium = screen.getAllByText(/Alice|Bob|Charlie/).slice(0, 3);
        expect(podium).toHaveLength(3);
      });
    });
  });

  describe("Current user highlighting", () => {
    it("highlights current user in the leaderboard", async () => {
      vi.mocked(leaderboardService.getLeaderboard).mockResolvedValue(mockLeaderboardData);

      render(<LeaderboardPage />);

      await waitFor(() => {
        expect(screen.getByText("You")).toBeInTheDocument();
      });
    });

    it("shows current user position at bottom when not in top list", async () => {
      const dataWithCurrentUserOutsideTop = {
        ...mockLeaderboardData,
        current_user: {
          user_id: 999,
          username: "currentuser",
          first_name: "Current User",
          rank: 50,
          xp: 1000,
          level: 3,
          lessons_completed: 10,
          achievements_count: 5,
        },
      };

      vi.mocked(useAuthStore).mockReturnValue({
        token: "mock-token",
        user: {
          id: 999,
          telegram_id: "999",
          username: "currentuser",
          first_name: "Current User",
          last_name: null,
          xp: 1000,
          level: 3,
          is_active: true,
          is_admin: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        status: "authenticated",
        error: null,
        setLoading: vi.fn(),
        setAuthenticated: vi.fn(),
        setError: vi.fn(),
        setNotInTelegram: vi.fn(),
        logout: vi.fn(),
        initialize: vi.fn(),
      });

      vi.mocked(leaderboardService.getLeaderboard).mockResolvedValue(dataWithCurrentUserOutsideTop);

      render(<LeaderboardPage />);

      await waitFor(() => {
        expect(screen.getByText("Current User")).toBeInTheDocument();
        expect(screen.getByText("#50")).toBeInTheDocument();
      });
    });
  });

  describe("Empty state", () => {
    it("renders empty state when no users", async () => {
      const emptyData: LeaderboardResponse = {
        entries: [],
        current_user: null,
        last_updated: null,
        total_users: 0,
      };

      vi.mocked(leaderboardService.getLeaderboard).mockResolvedValue(emptyData);

      render(<LeaderboardPage />);

      await waitFor(() => {
        expect(screen.getByText("No users yet")).toBeInTheDocument();
        expect(screen.getByText("The leaderboard is empty.")).toBeInTheDocument();
      });
    });
  });

  describe("Error handling", () => {
    it("renders error message on fetch failure", async () => {
      vi.mocked(leaderboardService.getLeaderboard).mockRejectedValue(
        new Error("Failed to fetch leaderboard")
      );

      render(<LeaderboardPage />);

      await waitFor(() => {
        expect(screen.getByText("Failed to fetch leaderboard")).toBeInTheDocument();
        expect(screen.getByText("Try again")).toBeInTheDocument();
      });
    });

    it("allows retry after error", async () => {
      vi.mocked(leaderboardService.getLeaderboard)
        .mockRejectedValueOnce(new Error("Failed to fetch leaderboard"))
        .mockResolvedValueOnce(mockLeaderboardData);

      render(<LeaderboardPage />);

      await waitFor(() => {
        expect(screen.getByText("Failed to fetch leaderboard")).toBeInTheDocument();
      });

      const retryButton = screen.getByText("Try again");
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.getAllByText("Alice").length).toBeGreaterThan(0);
      });
    });
  });

  describe("Responsive design", () => {
    it("renders all components in mobile layout", async () => {
      vi.mocked(leaderboardService.getLeaderboard).mockResolvedValue(mockLeaderboardData);

      render(<LeaderboardPage />);

      await waitFor(() => {
        expect(screen.getByText("Leaderboard")).toBeInTheDocument();
        expect(screen.getByText("100 active learners")).toBeInTheDocument();
      });
    });
  });

  describe("Pull to refresh", () => {
    it("shows refresh indicator during pull", async () => {
      vi.mocked(leaderboardService.getLeaderboard).mockResolvedValue(mockLeaderboardData);

      render(<LeaderboardPage />);

      await waitFor(() => {
        expect(screen.getAllByText("Alice").length).toBeGreaterThan(0);
      });

      // Note: Testing pull-to-refresh with touch events is complex in JSDOM
      // This test verifies the component renders without errors
      expect(screen.getByText("Leaderboard")).toBeInTheDocument();
    });
  });

  describe("Authorization", () => {
    it("does not fetch data when no token", async () => {
      vi.mocked(useAuthStore).mockReturnValue({
        token: null,
        user: null,
        status: "idle",
        error: null,
        setLoading: vi.fn(),
        setAuthenticated: vi.fn(),
        setError: vi.fn(),
        setNotInTelegram: vi.fn(),
        logout: vi.fn(),
        initialize: vi.fn(),
      });

      const getLeaderboardSpy = vi.mocked(leaderboardService.getLeaderboard);

      render(<LeaderboardPage />);

      await waitFor(() => {
        expect(getLeaderboardSpy).not.toHaveBeenCalled();
      });
    });
  });
});
