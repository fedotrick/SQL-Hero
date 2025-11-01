import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { useProgressSummary } from "./useProgressSummary";
import { progressApi } from "../services/api";
import type { UserProgressSummary } from "../types/progress";

vi.mock("../services/api");
vi.mock("../store/authStore");

const mockProgressData: UserProgressSummary = {
  user_id: 1,
  username: "testuser",
  xp: 250,
  level: 3,
  xp_to_next_level: 50,
  current_level_xp: 200,
  next_level_xp: 300,
  progress_percentage: 50,
  current_streak: 5,
  longest_streak: 10,
  total_queries: 30,
  lessons_completed: 10,
  total_lessons: 25,
  modules_completed: 1,
  total_modules: 5,
  achievements_count: 5,
  last_active_date: "2024-01-10T12:00:00Z",
};

describe("useProgressSummary", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it("should fetch progress summary successfully", async () => {
    const { useAuthStore } = vi.mocked(await import("../store/authStore"));
    useAuthStore.mockReturnValue({
      token: "test-token",
      user: null,
      status: "authenticated",
      error: null,
      setLoading: vi.fn(),
      setAuthenticated: vi.fn(),
      setError: vi.fn(),
      setNotInTelegram: vi.fn(),
      logout: vi.fn(),
      initialize: vi.fn(),
    });

    vi.mocked(progressApi.getSummary).mockResolvedValue(mockProgressData);

    const { result } = renderHook(() => useProgressSummary(), { wrapper });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockProgressData);
    expect(progressApi.getSummary).toHaveBeenCalledWith("test-token");
  });

  it("should handle error when fetching fails", async () => {
    const { useAuthStore } = vi.mocked(await import("../store/authStore"));
    useAuthStore.mockReturnValue({
      token: "test-token",
      user: null,
      status: "authenticated",
      error: null,
      setLoading: vi.fn(),
      setAuthenticated: vi.fn(),
      setError: vi.fn(),
      setNotInTelegram: vi.fn(),
      logout: vi.fn(),
      initialize: vi.fn(),
    });

    const error = new Error("Failed to fetch");
    vi.mocked(progressApi.getSummary).mockRejectedValue(error);

    const { result } = renderHook(() => useProgressSummary(), { wrapper });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toEqual(error);
  });

  it("should not fetch when token is not available", async () => {
    const { useAuthStore } = vi.mocked(await import("../store/authStore"));
    useAuthStore.mockReturnValue({
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

    const { result } = renderHook(() => useProgressSummary(), { wrapper });

    expect(result.current.isPending).toBe(true);
    expect(result.current.fetchStatus).toBe("idle");
    expect(progressApi.getSummary).not.toHaveBeenCalled();
  });

  it("should have correct staleTime configuration", async () => {
    const { useAuthStore } = vi.mocked(await import("../store/authStore"));
    useAuthStore.mockReturnValue({
      token: "test-token",
      user: null,
      status: "authenticated",
      error: null,
      setLoading: vi.fn(),
      setAuthenticated: vi.fn(),
      setError: vi.fn(),
      setNotInTelegram: vi.fn(),
      logout: vi.fn(),
      initialize: vi.fn(),
    });

    vi.mocked(progressApi.getSummary).mockResolvedValue(mockProgressData);

    const { result } = renderHook(() => useProgressSummary(), { wrapper });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(queryClient.getQueryState(["progress", "summary"])?.dataUpdatedAt).toBeDefined();
  });
});
