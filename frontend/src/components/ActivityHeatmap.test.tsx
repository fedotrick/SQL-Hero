import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ActivityHeatmap } from "./ActivityHeatmap";
import type { ActivityHeatmapEntry } from "../types/progress";

describe("ActivityHeatmap", () => {
  const mockData: ActivityHeatmapEntry[] = [
    { date: "2024-01-01", count: 0 },
    { date: "2024-01-02", count: 2 },
    { date: "2024-01-03", count: 5 },
    { date: "2024-01-04", count: 8 },
    { date: "2024-01-05", count: 3 },
    { date: "2024-01-06", count: 1 },
    { date: "2024-01-07", count: 0 },
  ];

  it("should render heatmap with data", () => {
    render(<ActivityHeatmap data={mockData} />);

    expect(screen.getByText("Less")).toBeInTheDocument();
    expect(screen.getByText("More")).toBeInTheDocument();
  });

  it("should render correct number of cells", () => {
    const { container } = render(<ActivityHeatmap data={mockData} />);

    const cells = container.querySelectorAll('[class*="w-3 h-3"]');
    expect(cells.length).toBeGreaterThan(mockData.length);
  });

  it("should apply different colors based on activity count", () => {
    const { container } = render(<ActivityHeatmap data={mockData} />);

    const cells = container.querySelectorAll('[class*="rounded-sm"]');
    const cellsArray = Array.from(cells);

    const hasZeroActivity = cellsArray.some((cell) =>
      cell.className.includes("bg-telegram-section-bg")
    );
    expect(hasZeroActivity).toBe(true);
  });

  it("should display recent 84 days when more data is provided", () => {
    const largeMockData: ActivityHeatmapEntry[] = Array.from(
      { length: 100 },
      (_, i) => ({
        date: `2024-01-${String(i + 1).padStart(2, "0")}`,
        count: Math.floor(Math.random() * 10),
      })
    );

    const { container } = render(<ActivityHeatmap data={largeMockData} />);

    const weeks = container.querySelectorAll('[class*="flex flex-col"]');
    expect(weeks.length).toBeLessThanOrEqual(12);
  });

  it("should show title on hover with activity count", () => {
    const { container } = render(<ActivityHeatmap data={mockData} />);

    const cells = container.querySelectorAll('[title]');
    const firstCellWithTitle = Array.from(cells).find((cell) =>
      cell.getAttribute("title")?.includes("2024-01-02")
    );

    expect(firstCellWithTitle).toBeDefined();
    expect(firstCellWithTitle?.getAttribute("title")).toContain("2");
    expect(firstCellWithTitle?.getAttribute("title")).toContain("activities");
  });

  it("should render intensity legend", () => {
    const { container } = render(<ActivityHeatmap data={mockData} />);

    const legend = container.querySelectorAll('.text-telegram-hint [class*="w-3 h-3"]');
    expect(legend.length).toBe(5);
  });

  it("should handle empty data", () => {
    render(<ActivityHeatmap data={[]} />);

    expect(screen.getByText("Less")).toBeInTheDocument();
    expect(screen.getByText("More")).toBeInTheDocument();
  });

  it("should respect custom maxCount", () => {
    const customMaxCount = 100;
    render(<ActivityHeatmap data={mockData} maxCount={customMaxCount} />);

    expect(screen.getByText("Less")).toBeInTheDocument();
  });
});
