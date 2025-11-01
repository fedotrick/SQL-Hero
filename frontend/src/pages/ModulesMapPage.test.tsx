import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderWithProviders as render, screen, waitFor } from "../test/utils";
import { ModulesMapPage } from "./ModulesMapPage";
import { coursesService } from "../services/courses";
import { useAuthStore } from "../store/authStore";
import type { ModuleListResponse } from "../types/courses";

vi.mock("../services/courses");
vi.mock("../store/authStore");
vi.mock("../services/telegramHaptics", () => ({
  telegramHaptics: {
    light: vi.fn(),
    error: vi.fn(),
  },
}));

describe("ModulesMapPage", () => {
  const mockModules: ModuleListResponse = {
    items: [
      {
        id: 1,
        title: "Module 1",
        description: "First module",
        order: 1,
        is_published: true,
        is_locked: false,
        lessons_count: 10,
        completed_lessons_count: 10,
      },
      {
        id: 2,
        title: "Module 2",
        description: "Second module",
        order: 2,
        is_published: true,
        is_locked: false,
        lessons_count: 8,
        completed_lessons_count: 4,
      },
      {
        id: 3,
        title: "Module 3",
        description: "Third module",
        order: 3,
        is_published: true,
        is_locked: true,
        lessons_count: 5,
        completed_lessons_count: 0,
      },
    ],
    total: 3,
    page: 1,
    page_size: 20,
    total_pages: 1,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useAuthStore).mockReturnValue({
      token: "mock-token",
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
  });

  it("renders loading screen initially", () => {
    vi.mocked(coursesService.getModules).mockImplementation(() => new Promise(() => {}));

    render(<ModulesMapPage />);
    expect(screen.getByText("Authenticating...")).toBeInTheDocument();
  });

  it("renders modules list after successful fetch", async () => {
    vi.mocked(coursesService.getModules).mockResolvedValue(mockModules);

    render(<ModulesMapPage />);

    await waitFor(() => {
      expect(screen.getByText("Module 1")).toBeInTheDocument();
      expect(screen.getByText("Module 2")).toBeInTheDocument();
      expect(screen.getByText("Module 3")).toBeInTheDocument();
    });
  });

  it("renders error message on fetch failure", async () => {
    vi.mocked(coursesService.getModules).mockRejectedValue(new Error("Failed to fetch modules"));

    render(<ModulesMapPage />);

    await waitFor(() => {
      expect(screen.getByText("Ошибка")).toBeInTheDocument();
      expect(screen.getByText("Failed to fetch modules")).toBeInTheDocument();
    });
  });

  it("shows not authorized error when token is missing", async () => {
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

    render(<ModulesMapPage />);

    await waitFor(() => {
      expect(screen.getByText("Не авторизован")).toBeInTheDocument();
    });
  });

  it("displays all filter options", async () => {
    vi.mocked(coursesService.getModules).mockResolvedValue(mockModules);

    render(<ModulesMapPage />);

    await waitFor(() => {
      expect(screen.getByText("Все")).toBeInTheDocument();
      expect(screen.getByText("Доступные")).toBeInTheDocument();
      expect(screen.getByText("В процессе")).toBeInTheDocument();
      expect(screen.getByText("Завершенные")).toBeInTheDocument();
    });
  });

  it("renders legend with status icons", async () => {
    vi.mocked(coursesService.getModules).mockResolvedValue(mockModules);

    render(<ModulesMapPage />);

    await waitFor(() => {
      expect(screen.getByText("Легенда:")).toBeInTheDocument();
      expect(screen.getByText("Модуль заблокирован")).toBeInTheDocument();
      expect(screen.getByText("Модуль доступен")).toBeInTheDocument();
      expect(screen.getByText("Модуль в процессе")).toBeInTheDocument();
      expect(screen.getByText("Модуль завершен")).toBeInTheDocument();
    });
  });

  it("displays correct number of modules", async () => {
    vi.mocked(coursesService.getModules).mockResolvedValue(mockModules);

    render(<ModulesMapPage />);

    await waitFor(() => {
      const modules = screen.getAllByText(/Module \d/);
      expect(modules).toHaveLength(3);
    });
  });

  it("shows tooltips for locked modules", async () => {
    vi.mocked(coursesService.getModules).mockResolvedValue(mockModules);

    render(<ModulesMapPage />);

    await waitFor(() => {
      const tooltip = screen.getByText(/Завершите предыдущий модуль, чтобы разблокировать/);
      expect(tooltip).toBeInTheDocument();
    });
  });
});
