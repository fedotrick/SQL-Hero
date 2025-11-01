import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "../test/utils";
import userEvent from "@testing-library/user-event";
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

describe("ModulesMapPage Integration", () => {
  const mockModules: ModuleListResponse = {
    items: [
      {
        id: 1,
        title: "Completed Module",
        description: "Fully completed",
        order: 1,
        is_published: true,
        is_locked: false,
        lessons_count: 10,
        completed_lessons_count: 10,
      },
      {
        id: 2,
        title: "In Progress Module",
        description: "Partially completed",
        order: 2,
        is_published: true,
        is_locked: false,
        lessons_count: 8,
        completed_lessons_count: 4,
      },
      {
        id: 3,
        title: "Available Module",
        description: "Not started",
        order: 3,
        is_published: true,
        is_locked: false,
        lessons_count: 5,
        completed_lessons_count: 0,
      },
      {
        id: 4,
        title: "Locked Module",
        description: "Not accessible",
        order: 4,
        is_published: true,
        is_locked: true,
        lessons_count: 6,
        completed_lessons_count: 0,
      },
    ],
    total: 4,
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
    vi.mocked(coursesService.getModules).mockResolvedValue(mockModules);
  });

  it("filters modules by available status", async () => {
    const user = userEvent.setup();

    render(<ModulesMapPage />);

    await waitFor(() => {
      expect(screen.getByText("Completed Module")).toBeInTheDocument();
    });

    const availableFilter = screen.getByText("Доступные");
    await user.click(availableFilter);

    expect(screen.getByText("Available Module")).toBeInTheDocument();
    expect(screen.queryByText("Completed Module")).not.toBeInTheDocument();
    expect(screen.queryByText("In Progress Module")).not.toBeInTheDocument();
    expect(screen.queryByText("Locked Module")).not.toBeInTheDocument();
  });

  it("filters modules by in-progress status", async () => {
    const user = userEvent.setup();

    render(<ModulesMapPage />);

    await waitFor(() => {
      expect(screen.getByText("In Progress Module")).toBeInTheDocument();
    });

    const inProgressFilter = screen.getByText("В процессе");
    await user.click(inProgressFilter);

    expect(screen.getByText("In Progress Module")).toBeInTheDocument();
    expect(screen.queryByText("Completed Module")).not.toBeInTheDocument();
    expect(screen.queryByText("Available Module")).not.toBeInTheDocument();
    expect(screen.queryByText("Locked Module")).not.toBeInTheDocument();
  });

  it("filters modules by completed status", async () => {
    const user = userEvent.setup();

    render(<ModulesMapPage />);

    await waitFor(() => {
      expect(screen.getByText("Completed Module")).toBeInTheDocument();
    });

    const completedFilter = screen.getByText("Завершенные");
    await user.click(completedFilter);

    expect(screen.getByText("Completed Module")).toBeInTheDocument();
    expect(screen.queryByText("In Progress Module")).not.toBeInTheDocument();
    expect(screen.queryByText("Available Module")).not.toBeInTheDocument();
    expect(screen.queryByText("Locked Module")).not.toBeInTheDocument();
  });

  it("shows all modules when 'all' filter is selected", async () => {
    const user = userEvent.setup();

    render(<ModulesMapPage />);

    await waitFor(() => {
      expect(screen.getByText("Completed Module")).toBeInTheDocument();
    });

    const completedFilter = screen.getByText("Завершенные");
    await user.click(completedFilter);

    const allFilter = screen.getByText("Все");
    await user.click(allFilter);

    expect(screen.getByText("Completed Module")).toBeInTheDocument();
    expect(screen.getByText("In Progress Module")).toBeInTheDocument();
    expect(screen.getByText("Available Module")).toBeInTheDocument();
    expect(screen.getByText("Locked Module")).toBeInTheDocument();
  });

  it("shows correct status icons for each module type", async () => {
    render(<ModulesMapPage />);

    await waitFor(() => {
      expect(screen.getByText("Completed Module")).toBeInTheDocument();
    });

    const icons = screen.getAllByRole("img");
    expect(icons.length).toBeGreaterThanOrEqual(4);
  });

  it("displays empty state when no modules match filter", async () => {
    const user = userEvent.setup();
    
    const emptyResponse: ModuleListResponse = {
      items: [
        {
          id: 1,
          title: "Only Locked Module",
          description: "Locked",
          order: 1,
          is_published: true,
          is_locked: true,
          lessons_count: 5,
          completed_lessons_count: 0,
        },
      ],
      total: 1,
      page: 1,
      page_size: 20,
      total_pages: 1,
    };

    vi.mocked(coursesService.getModules).mockResolvedValue(emptyResponse);

    render(<ModulesMapPage />);

    await waitFor(() => {
      expect(screen.getByText("Only Locked Module")).toBeInTheDocument();
    });

    const completedFilter = screen.getByText("Завершенные");
    await user.click(completedFilter);

    expect(screen.getByText("Модули не найдены")).toBeInTheDocument();
  });

  it("maintains filter state when switching between filters", async () => {
    const user = userEvent.setup();

    render(<ModulesMapPage />);

    await waitFor(() => {
      expect(screen.getByText("Completed Module")).toBeInTheDocument();
    });

    const availableFilter = screen.getByText("Доступные");
    await user.click(availableFilter);
    
    expect(screen.getByText("Available Module")).toBeInTheDocument();

    const inProgressFilter = screen.getByText("В процессе");
    await user.click(inProgressFilter);
    
    expect(screen.getByText("In Progress Module")).toBeInTheDocument();
    expect(screen.queryByText("Available Module")).not.toBeInTheDocument();
  });
});
