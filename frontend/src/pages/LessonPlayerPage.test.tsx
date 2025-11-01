import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { LessonPlayerPage } from "./LessonPlayerPage";
import { useAuthStore } from "../store/authStore";
import * as coursesService from "../services/courses";
import * as progressService from "../services/progress";
import type { LessonDetail } from "../types/courses";
import type { LessonAttemptResponse } from "../types/progress";

// Mock the services
vi.mock("../services/courses");
vi.mock("../services/progress");
vi.mock("../services/telegramHaptics", () => ({
  telegramHaptics: {
    light: vi.fn(),
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock the auth store
vi.mock("../store/authStore", () => ({
  useAuthStore: vi.fn(),
}));

const mockLesson: LessonDetail = {
  id: 1,
  module_id: 1,
  title: "Test Lesson",
  content: "This is a test lesson content.",
  theory: "This is the theory for the lesson.",
  sql_solution: "SELECT * FROM users;",
  expected_result: { columns: ["id", "name"], rows: [[1, "John"]] },
  order: 1,
  estimated_duration: 15,
  is_published: true,
  is_locked: false,
  progress_status: null,
  attempts: 0,
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

const mockAttemptResponse: LessonAttemptResponse = {
  success: true,
  xp_earned: 75,
  total_xp: 75,
  level: 1,
  level_up: false,
  current_streak: 1,
  longest_streak: 1,
  attempts: 1,
  first_try: true,
  progress_status: "completed",
  message: "Отлично! Вы правильно решили задачу.",
  achievements_unlocked: [],
};

describe("LessonPlayerPage", () => {
  beforeEach(() => {
    vi.mocked(useAuthStore).mockReturnValue({
      token: "test-token",
      user: null,
      setToken: vi.fn(),
      setUser: vi.fn(),
      logout: vi.fn(),
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("should render loading state initially", () => {
    vi.mocked(coursesService.coursesService.getLessonDetail).mockImplementation(
      () => new Promise(() => {})
    );

    render(
      <MemoryRouter initialEntries={["/lessons/1"]}>
        <Routes>
          <Route path="/lessons/:lessonId" element={<LessonPlayerPage />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText(/загрузка/i)).toBeInTheDocument();
  });

  it("should render error state when lesson fetch fails", async () => {
    vi.mocked(coursesService.coursesService.getLessonDetail).mockRejectedValue(
      new Error("Failed to load lesson")
    );

    render(
      <MemoryRouter initialEntries={["/lessons/1"]}>
        <Routes>
          <Route path="/lessons/:lessonId" element={<LessonPlayerPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/ошибка/i)).toBeInTheDocument();
      expect(screen.getByText(/failed to load lesson/i)).toBeInTheDocument();
    });
  });

  it("should render locked lesson message", async () => {
    const lockedLesson = { ...mockLesson, is_locked: true };
    vi.mocked(coursesService.coursesService.getLessonDetail).mockResolvedValue(lockedLesson);

    render(
      <MemoryRouter initialEntries={["/lessons/1"]}>
        <Routes>
          <Route path="/lessons/:lessonId" element={<LessonPlayerPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/урок заблокирован/i)).toBeInTheDocument();
    });
  });

  it("should render lesson with theory and content", async () => {
    vi.mocked(coursesService.coursesService.getLessonDetail).mockResolvedValue(mockLesson);

    render(
      <MemoryRouter initialEntries={["/lessons/1"]}>
        <Routes>
          <Route path="/lessons/:lessonId" element={<LessonPlayerPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Test Lesson")).toBeInTheDocument();
      expect(screen.getByText(/this is the theory/i)).toBeInTheDocument();
      expect(screen.getByText(/this is a test lesson content/i)).toBeInTheDocument();
    });
  });

  it("should display attempts count", async () => {
    const lessonWithAttempts = { ...mockLesson, attempts: 3 };
    vi.mocked(coursesService.coursesService.getLessonDetail).mockResolvedValue(
      lessonWithAttempts
    );

    render(
      <MemoryRouter initialEntries={["/lessons/1"]}>
        <Routes>
          <Route path="/lessons/:lessonId" element={<LessonPlayerPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/попыток: 3/i)).toBeInTheDocument();
    });
  });

  it("should allow user to type SQL query", async () => {
    vi.mocked(coursesService.coursesService.getLessonDetail).mockResolvedValue(mockLesson);

    render(
      <MemoryRouter initialEntries={["/lessons/1"]}>
        <Routes>
          <Route path="/lessons/:lessonId" element={<LessonPlayerPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      const textarea = screen.getByPlaceholderText(/введите ваш sql запрос/i);
      expect(textarea).toBeInTheDocument();
      fireEvent.change(textarea, { target: { value: "SELECT * FROM users;" } });
      expect(textarea).toHaveValue("SELECT * FROM users;");
    });
  });

  it("should submit query and show success result", async () => {
    vi.mocked(coursesService.coursesService.getLessonDetail).mockResolvedValue(mockLesson);
    vi.mocked(progressService.progressService.submitLessonAttempt).mockResolvedValue(
      mockAttemptResponse
    );

    render(
      <MemoryRouter initialEntries={["/lessons/1"]}>
        <Routes>
          <Route path="/lessons/:lessonId" element={<LessonPlayerPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      const textarea = screen.getByPlaceholderText(/введите ваш sql запрос/i);
      fireEvent.change(textarea, { target: { value: "SELECT * FROM users;" } });
    });

    const runButton = screen.getByRole("button", { name: /запустить/i });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText(/правильно/i)).toBeInTheDocument();
      expect(screen.getByText(/\+75 XP/i)).toBeInTheDocument();
      expect(screen.getByText(/первая попытка/i)).toBeInTheDocument();
    });
  });

  it("should submit query and show error result", async () => {
    const failedResponse = {
      ...mockAttemptResponse,
      success: false,
      xp_earned: 0,
      first_try: false,
      progress_status: "in_progress",
      message: "Запрос неверный. Попробуйте еще раз.",
    };

    vi.mocked(coursesService.coursesService.getLessonDetail).mockResolvedValue(mockLesson);
    vi.mocked(progressService.progressService.submitLessonAttempt).mockResolvedValue(
      failedResponse
    );

    render(
      <MemoryRouter initialEntries={["/lessons/1"]}>
        <Routes>
          <Route path="/lessons/:lessonId" element={<LessonPlayerPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      const textarea = screen.getByPlaceholderText(/введите ваш sql запрос/i);
      fireEvent.change(textarea, { target: { value: "INVALID SQL" } });
    });

    const runButton = screen.getByRole("button", { name: /запустить/i });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText(/попробуйте еще раз/i)).toBeInTheDocument();
      expect(screen.getByText(/запрос неверный/i)).toBeInTheDocument();
    });
  });

  it("should show level up message when user levels up", async () => {
    const levelUpResponse = {
      ...mockAttemptResponse,
      level: 2,
      level_up: true,
    };

    vi.mocked(coursesService.coursesService.getLessonDetail).mockResolvedValue(mockLesson);
    vi.mocked(progressService.progressService.submitLessonAttempt).mockResolvedValue(
      levelUpResponse
    );

    render(
      <MemoryRouter initialEntries={["/lessons/1"]}>
        <Routes>
          <Route path="/lessons/:lessonId" element={<LessonPlayerPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      const textarea = screen.getByPlaceholderText(/введите ваш sql запрос/i);
      fireEvent.change(textarea, { target: { value: "SELECT * FROM users;" } });
    });

    const runButton = screen.getByRole("button", { name: /запустить/i });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText(/новый уровень: 2/i)).toBeInTheDocument();
    });
  });

  it("should show achievements when unlocked", async () => {
    const achievementResponse = {
      ...mockAttemptResponse,
      achievements_unlocked: [
        {
          achievement_id: 1,
          code: "first_lesson",
          title: "Первый урок",
          icon: "🏆",
          points: 10,
        },
      ],
    };

    vi.mocked(coursesService.coursesService.getLessonDetail).mockResolvedValue(mockLesson);
    vi.mocked(progressService.progressService.submitLessonAttempt).mockResolvedValue(
      achievementResponse
    );

    render(
      <MemoryRouter initialEntries={["/lessons/1"]}>
        <Routes>
          <Route path="/lessons/:lessonId" element={<LessonPlayerPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      const textarea = screen.getByPlaceholderText(/введите ваш sql запрос/i);
      fireEvent.change(textarea, { target: { value: "SELECT * FROM users;" } });
    });

    const runButton = screen.getByRole("button", { name: /запустить/i });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText(/разблокированы достижения/i)).toBeInTheDocument();
      expect(screen.getByText(/первый урок/i)).toBeInTheDocument();
    });
  });

  it("should disable run button when query is empty", async () => {
    vi.mocked(coursesService.coursesService.getLessonDetail).mockResolvedValue(mockLesson);

    render(
      <MemoryRouter initialEntries={["/lessons/1"]}>
        <Routes>
          <Route path="/lessons/:lessonId" element={<LessonPlayerPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      const runButton = screen.getByRole("button", { name: /запустить/i });
      expect(runButton).toBeDisabled();
    });
  });

  it("should handle submission error gracefully", async () => {
    vi.mocked(coursesService.coursesService.getLessonDetail).mockResolvedValue(mockLesson);
    vi.mocked(progressService.progressService.submitLessonAttempt).mockRejectedValue(
      new Error("Network error")
    );

    render(
      <MemoryRouter initialEntries={["/lessons/1"]}>
        <Routes>
          <Route path="/lessons/:lessonId" element={<LessonPlayerPage />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      const textarea = screen.getByPlaceholderText(/введите ваш sql запрос/i);
      fireEvent.change(textarea, { target: { value: "SELECT * FROM users;" } });
    });

    const runButton = screen.getByRole("button", { name: /запустить/i });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getByText(/network error/i)).toBeInTheDocument();
    });
  });
});
