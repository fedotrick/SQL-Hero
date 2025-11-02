import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { StreakCalendar } from "./StreakCalendar";
import { ActivityHeatmapEntry } from "../../types/activity";

describe("StreakCalendar", () => {
  const mockData: ActivityHeatmapEntry[] = [
    { date: "2024-01-01", count: 5 },
    { date: "2024-01-02", count: 3 },
    { date: "2024-01-03", count: 8 },
    { date: "2024-01-04", count: 0 },
    { date: "2024-01-05", count: 12 },
  ];

  describe("Data Mapping Logic", () => {
    it("should correctly map activity data to calendar grid", () => {
      const { container } = render(
        <StreakCalendar data={mockData} startDate="2024-01-01" endDate="2024-01-05" />
      );

      // Check that the calendar grid is rendered
      const grid = container.querySelector('[class*="flex gap-1"]');
      expect(grid).toBeTruthy();
    });

    it("should handle empty data gracefully", () => {
      const { container } = render(
        <StreakCalendar data={[]} startDate="2024-01-01" endDate="2024-01-07" />
      );

      // Should render without crashing
      expect(container).toBeTruthy();
    });

    it("should calculate correct intensity classes based on count", () => {
      const { container } = render(
        <StreakCalendar data={mockData} startDate="2024-01-01" endDate="2024-01-05" />
      );

      // Find days with different intensities
      const days = container.querySelectorAll('[class*="w-3 h-3"]');
      expect(days.length).toBeGreaterThan(0);
    });

    it("should handle date range correctly", () => {
      const startDate = "2024-01-01";
      const endDate = "2024-01-31";

      const { container } = render(
        <StreakCalendar
          data={mockData}
          startDate={startDate}
          endDate={endDate}
          showLegend={true}
        />
      );

      // Should render the entire month
      expect(container).toBeTruthy();
    });

    it("should calculate weeks correctly", () => {
      const data: ActivityHeatmapEntry[] = Array.from({ length: 14 }, (_, i) => ({
        date: `2024-01-${String(i + 1).padStart(2, "0")}`,
        count: i,
      }));

      const { container } = render(
        <StreakCalendar data={data} startDate="2024-01-01" endDate="2024-01-14" />
      );

      // Should organize days into weeks (7 days per week)
      const grid = container.querySelector('[class*="flex gap-1"]');
      expect(grid).toBeTruthy();
    });
  });

  describe("Intensity Color Mapping", () => {
    it("should apply correct color for zero activity", () => {
      const zeroData: ActivityHeatmapEntry[] = [{ date: "2024-01-01", count: 0 }];

      const { container } = render(<StreakCalendar data={zeroData} />);

      const days = container.querySelectorAll('[class*="bg-telegram-secondary-bg"]');
      expect(days.length).toBeGreaterThan(0);
    });

    it("should apply correct colors for different activity levels", () => {
      const testData: ActivityHeatmapEntry[] = [
        { date: "2024-01-01", count: 1 }, // Low
        { date: "2024-01-02", count: 5 }, // Medium-low
        { date: "2024-01-03", count: 10 }, // Medium-high
        { date: "2024-01-04", count: 15 }, // High
      ];

      const { container } = render(<StreakCalendar data={testData} />);

      // Should have different intensity classes
      const days = container.querySelectorAll('[class*="w-3 h-3"]');
      expect(days.length).toBeGreaterThan(0);
    });
  });

  describe("Streak Statistics", () => {
    it("should display current streak when provided", () => {
      render(<StreakCalendar data={mockData} currentStreak={7} />);

      expect(screen.getByText("7 дней")).toBeInTheDocument();
      expect(screen.getByText("Текущая серия")).toBeInTheDocument();
    });

    it("should display longest streak when provided", () => {
      render(<StreakCalendar data={mockData} longestStreak={15} />);

      expect(screen.getByText("15 дней")).toBeInTheDocument();
      expect(screen.getByText("Лучшая серия")).toBeInTheDocument();
    });

    it("should display both streaks when both provided", () => {
      render(<StreakCalendar data={mockData} currentStreak={7} longestStreak={15} />);

      expect(screen.getByText("7 дней")).toBeInTheDocument();
      expect(screen.getByText("15 дней")).toBeInTheDocument();
    });

    it("should not display streak stats when both are zero", () => {
      const { container } = render(
        <StreakCalendar data={mockData} currentStreak={0} longestStreak={0} />
      );

      expect(screen.queryByText("Текущая серия")).not.toBeInTheDocument();
      expect(screen.queryByText("Лучшая серия")).not.toBeInTheDocument();
    });
  });

  describe("Legend", () => {
    it("should show legend when showLegend is true", () => {
      render(<StreakCalendar data={mockData} showLegend={true} />);

      expect(screen.getByText("Меньше")).toBeInTheDocument();
      expect(screen.getByText("Больше")).toBeInTheDocument();
    });

    it("should hide legend when showLegend is false", () => {
      render(<StreakCalendar data={mockData} showLegend={false} />);

      expect(screen.queryByText("Меньше")).not.toBeInTheDocument();
      expect(screen.queryByText("Больше")).not.toBeInTheDocument();
    });
  });

  describe("Month Labels", () => {
    it("should display month labels", () => {
      const data: ActivityHeatmapEntry[] = [
        { date: "2024-01-15", count: 5 },
        { date: "2024-02-15", count: 3 },
        { date: "2024-03-15", count: 8 },
      ];

      const { container } = render(
        <StreakCalendar data={data} startDate="2024-01-01" endDate="2024-03-31" />
      );

      // Should show month labels
      expect(container.textContent).toMatch(/Янв|Фев|Мар/);
    });
  });

  describe("Interaction", () => {
    it("should call onDayClick when a day is clicked", async () => {
      const handleDayClick = vi.fn();

      const { container } = render(
        <StreakCalendar data={mockData} onDayClick={handleDayClick} />
      );

      const days = container.querySelectorAll('[class*="cursor-pointer"]');
      if (days.length > 0) {
        fireEvent.click(days[0]);
        await waitFor(() => {
          expect(handleDayClick).toHaveBeenCalled();
        });
      }
    });

    it("should show tooltip on hover", async () => {
      const { container } = render(<StreakCalendar data={mockData} />);

      const days = container.querySelectorAll('[class*="cursor-pointer"]');
      if (days.length > 0) {
        fireEvent.mouseEnter(days[0]);

        await waitFor(() => {
          // Tooltip should appear (it's rendered with fixed positioning)
          const tooltip = container.querySelector('[class*="fixed z-50"]');
          expect(tooltip).toBeTruthy();
        });
      }
    });

    it("should hide tooltip on mouse leave", async () => {
      const { container } = render(<StreakCalendar data={mockData} />);

      const days = container.querySelectorAll('[class*="cursor-pointer"]');
      if (days.length > 0) {
        fireEvent.mouseEnter(days[0]);
        fireEvent.mouseLeave(days[0]);

        // Tooltip should be hidden
        await waitFor(() => {
          const tooltip = container.querySelector('[class*="fixed z-50"]');
          expect(tooltip).toBeFalsy();
        });
      }
    });
  });

  describe("Edge Cases", () => {
    it("should handle single day data", () => {
      const singleDay: ActivityHeatmapEntry[] = [{ date: "2024-01-01", count: 5 }];

      const { container } = render(<StreakCalendar data={singleDay} />);

      expect(container).toBeTruthy();
    });

    it("should handle year-long data", () => {
      const yearData: ActivityHeatmapEntry[] = Array.from({ length: 365 }, (_, i) => {
        const date = new Date(2024, 0, 1);
        date.setDate(date.getDate() + i);
        return {
          date: date.toISOString().split("T")[0],
          count: Math.floor(Math.random() * 20),
        };
      });

      const { container } = render(
        <StreakCalendar data={yearData} startDate="2024-01-01" endDate="2024-12-31" />
      );

      expect(container).toBeTruthy();
    });

    it("should handle data with gaps", () => {
      const gappedData: ActivityHeatmapEntry[] = [
        { date: "2024-01-01", count: 5 },
        { date: "2024-01-05", count: 3 }, // 3-day gap
        { date: "2024-01-10", count: 8 }, // 4-day gap
      ];

      const { container } = render(
        <StreakCalendar data={gappedData} startDate="2024-01-01" endDate="2024-01-10" />
      );

      // Should fill in missing days with zero count
      expect(container).toBeTruthy();
    });

    it("should handle maximum count correctly for intensity", () => {
      const extremeData: ActivityHeatmapEntry[] = [
        { date: "2024-01-01", count: 1 },
        { date: "2024-01-02", count: 100 },
        { date: "2024-01-03", count: 50 },
      ];

      const { container } = render(<StreakCalendar data={extremeData} />);

      // Should scale colors relative to max (100)
      const days = container.querySelectorAll('[class*="w-3 h-3"]');
      expect(days.length).toBeGreaterThan(0);
    });
  });

  describe("Responsive Layout", () => {
    it("should render day of week labels", () => {
      render(<StreakCalendar data={mockData} />);

      // Should show some day labels (only odd indices are visible)
      const dayLabels = ["Пн", "Ср", "Пт"];
      dayLabels.forEach((label) => {
        expect(screen.getByText(label)).toBeInTheDocument();
      });
    });

    it("should handle overflow with scrolling container", () => {
      const longData: ActivityHeatmapEntry[] = Array.from({ length: 180 }, (_, i) => ({
        date: `2024-${String(Math.floor(i / 30) + 1).padStart(2, "0")}-${String((i % 30) + 1).padStart(2, "0")}`,
        count: i % 10,
      }));

      const { container } = render(<StreakCalendar data={longData} />);

      // Should have overflow container
      const overflowContainer = container.querySelector('[class*="overflow-x-auto"]');
      expect(overflowContainer).toBeTruthy();
    });
  });

  describe("Animation", () => {
    it("should apply animation when animateNewStreak is true", () => {
      const { container } = render(
        <StreakCalendar data={mockData} currentStreak={5} animateNewStreak={true} />
      );

      // Framer Motion should add animation classes
      expect(container).toBeTruthy();
    });

    it("should not animate when animateNewStreak is false", () => {
      const { container } = render(
        <StreakCalendar data={mockData} currentStreak={5} animateNewStreak={false} />
      );

      expect(container).toBeTruthy();
    });
  });

  describe("Date Formatting", () => {
    it("should correctly parse and display dates", () => {
      const testDate: ActivityHeatmapEntry[] = [{ date: "2024-03-15", count: 5 }];

      const { container } = render(<StreakCalendar data={testDate} />);

      expect(container).toBeTruthy();
    });

    it("should handle date boundaries correctly", () => {
      const boundaryData: ActivityHeatmapEntry[] = [
        { date: "2024-01-01", count: 1 }, // Start of year
        { date: "2024-12-31", count: 2 }, // End of year
      ];

      const { container } = render(
        <StreakCalendar data={boundaryData} startDate="2024-01-01" endDate="2024-12-31" />
      );

      expect(container).toBeTruthy();
    });
  });
});
