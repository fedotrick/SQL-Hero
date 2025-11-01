import { describe, it, expect, vi } from "vitest";
import { render, screen } from "../../test/utils";
import userEvent from "@testing-library/user-event";
import { ModuleFilter } from "./ModuleFilter";

describe("ModuleFilter", () => {
  it("renders all filter options", () => {
    const handleFilterChange = vi.fn();

    render(<ModuleFilter activeFilter="all" onFilterChange={handleFilterChange} />);

    expect(screen.getByText("Все")).toBeInTheDocument();
    expect(screen.getByText("Доступные")).toBeInTheDocument();
    expect(screen.getByText("В процессе")).toBeInTheDocument();
    expect(screen.getByText("Завершенные")).toBeInTheDocument();
  });

  it("calls onFilterChange when filter is clicked", async () => {
    const user = userEvent.setup();
    const handleFilterChange = vi.fn();

    render(<ModuleFilter activeFilter="all" onFilterChange={handleFilterChange} />);

    await user.click(screen.getByText("Доступные"));

    expect(handleFilterChange).toHaveBeenCalledWith("available");
  });

  it("calls onFilterChange with correct filter value", async () => {
    const user = userEvent.setup();
    const handleFilterChange = vi.fn();

    render(<ModuleFilter activeFilter="all" onFilterChange={handleFilterChange} />);

    await user.click(screen.getByText("В процессе"));
    expect(handleFilterChange).toHaveBeenCalledWith("in-progress");

    await user.click(screen.getByText("Завершенные"));
    expect(handleFilterChange).toHaveBeenCalledWith("completed");
  });

  it("applies active style to active filter", () => {
    const handleFilterChange = vi.fn();

    render(<ModuleFilter activeFilter="available" onFilterChange={handleFilterChange} />);

    const availableButton = screen.getByText("Доступные");
    expect(availableButton).toBeInTheDocument();
  });

  it("allows switching between filters", async () => {
    const user = userEvent.setup();
    const handleFilterChange = vi.fn();

    const { rerender } = render(
      <ModuleFilter activeFilter="all" onFilterChange={handleFilterChange} />
    );

    await user.click(screen.getByText("Доступные"));
    expect(handleFilterChange).toHaveBeenCalledWith("available");

    rerender(<ModuleFilter activeFilter="available" onFilterChange={handleFilterChange} />);

    await user.click(screen.getByText("Завершенные"));
    expect(handleFilterChange).toHaveBeenCalledWith("completed");
  });
});
