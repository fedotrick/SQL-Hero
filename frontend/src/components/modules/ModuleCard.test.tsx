import { describe, it, expect, vi } from "vitest";
import { render, screen } from "../../test/utils";
import userEvent from "@testing-library/user-event";
import { ModuleCard } from "./ModuleCard";
import type { ModuleListItem } from "../../types/courses";

describe("ModuleCard", () => {
  const mockModule: ModuleListItem = {
    id: 1,
    title: "Test Module",
    description: "Test Description",
    order: 1,
    is_published: true,
    is_locked: false,
    lessons_count: 10,
    completed_lessons_count: 5,
  };

  it("renders module information correctly", () => {
    render(<ModuleCard module={mockModule} />);

    expect(screen.getByText("Test Module")).toBeInTheDocument();
    expect(screen.getByText("Test Description")).toBeInTheDocument();
    expect(screen.getByText("Уроков: 5/10")).toBeInTheDocument();
    expect(screen.getByText("50%")).toBeInTheDocument();
  });

  it("shows in-progress status icon for partially completed module", () => {
    render(<ModuleCard module={mockModule} />);

    const statusIcon = screen.getByRole("img");
    expect(statusIcon).toHaveTextContent("🟡");
  });

  it("shows completed status icon for fully completed module", () => {
    const completedModule = { ...mockModule, completed_lessons_count: 10 };
    render(<ModuleCard module={completedModule} />);

    const statusIcon = screen.getByRole("img");
    expect(statusIcon).toHaveTextContent("✅");
  });

  it("shows available status icon for unlocked module with no progress", () => {
    const availableModule = { ...mockModule, completed_lessons_count: 0 };
    render(<ModuleCard module={availableModule} />);

    const statusIcon = screen.getByRole("img");
    expect(statusIcon).toHaveTextContent("➡️");
  });

  it("shows locked status icon and lock icon for locked module", () => {
    const lockedModule = { ...mockModule, is_locked: true, completed_lessons_count: 0 };
    render(<ModuleCard module={lockedModule} />);

    const statusIcon = screen.getByRole("img");
    expect(statusIcon).toHaveTextContent("🔒");

    const lockIcon = document.querySelector("svg");
    expect(lockIcon).toBeInTheDocument();
  });

  it("shows tooltip when locked and showTooltip is true", () => {
    const lockedModule = { ...mockModule, is_locked: true };
    render(<ModuleCard module={lockedModule} showTooltip={true} />);

    expect(
      screen.getByText(/Завершите предыдущий модуль, чтобы разблокировать/)
    ).toBeInTheDocument();
  });

  it("does not show tooltip when locked but showTooltip is false", () => {
    const lockedModule = { ...mockModule, is_locked: true };
    render(<ModuleCard module={lockedModule} showTooltip={false} />);

    expect(
      screen.queryByText(/Завершите предыдущий модуль, чтобы разблокировать/)
    ).not.toBeInTheDocument();
  });

  it("calls onClick with module id when unlocked module is clicked", async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();

    render(<ModuleCard module={mockModule} onClick={handleClick} />);

    const card = screen.getByText("Test Module").closest("div");
    if (card) {
      await user.click(card);
      expect(handleClick).toHaveBeenCalledWith(1);
    }
  });

  it("does not call onClick when locked module is clicked", async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();
    const lockedModule = { ...mockModule, is_locked: true };

    render(<ModuleCard module={lockedModule} onClick={handleClick} />);

    const card = screen.getByText("Test Module").closest("div");
    if (card) {
      await user.click(card);
      expect(handleClick).not.toHaveBeenCalled();
    }
  });

  it("shows correct progress bar variant for completed module", () => {
    const completedModule = { ...mockModule, completed_lessons_count: 10 };
    const { container } = render(<ModuleCard module={completedModule} />);

    const progressBar = container.querySelector(".bg-green-500");
    expect(progressBar).toBeInTheDocument();
  });

  it("calculates progress percentage correctly", () => {
    const module25Percent = { ...mockModule, lessons_count: 8, completed_lessons_count: 2 };
    render(<ModuleCard module={module25Percent} />);

    expect(screen.getByText("25%")).toBeInTheDocument();
  });

  it("shows 0% for module with no lessons", () => {
    const moduleNoLessons = { ...mockModule, lessons_count: 0, completed_lessons_count: 0 };
    render(<ModuleCard module={moduleNoLessons} />);

    expect(screen.getByText("0%")).toBeInTheDocument();
  });

  it("applies opacity style to locked modules", () => {
    const lockedModule = { ...mockModule, is_locked: true };
    const { container } = render(<ModuleCard module={lockedModule} />);

    const card = container.querySelector(".opacity-60");
    expect(card).toBeInTheDocument();
  });
});
