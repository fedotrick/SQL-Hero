import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ResultTable } from "./ResultTable";

describe("ResultTable", () => {
  const mockResult = [
    { id: 1, name: "John Doe", email: "john@example.com" },
    { id: 2, name: "Jane Smith", email: "jane@example.com" },
  ];

  const mockExpectedResult = [
    { id: 1, name: "John Doe", email: "john@example.com" },
    { id: 2, name: "Jane Smith", email: "jane@example.com" },
  ];

  const mockMismatchedResult = [
    { id: 1, name: "Wrong Name", email: "wrong@example.com" },
    { id: 2, name: "Jane Smith", email: "jane@example.com" },
  ];

  it("renders table with results", () => {
    render(<ResultTable result={mockResult} />);

    expect(screen.getByText("John Doe")).toBeInTheDocument();
    expect(screen.getByText("Jane Smith")).toBeInTheDocument();
    expect(screen.getByText("john@example.com")).toBeInTheDocument();
    expect(screen.getByText("jane@example.com")).toBeInTheDocument();
  });

  it("renders column headers", () => {
    render(<ResultTable result={mockResult} />);

    expect(screen.getByText("id")).toBeInTheDocument();
    expect(screen.getByText("name")).toBeInTheDocument();
    expect(screen.getByText("email")).toBeInTheDocument();
  });

  it("displays correct row count", () => {
    render(<ResultTable result={mockResult} />);

    expect(screen.getByText("2 строки")).toBeInTheDocument();
  });

  it("displays 'строка' for single row", () => {
    const singleResult = [{ id: 1, name: "John Doe" }];
    render(<ResultTable result={singleResult} />);

    expect(screen.getByText("1 строка")).toBeInTheDocument();
  });

  it("displays 'строк' for 5 or more rows", () => {
    const manyResults = Array.from({ length: 5 }, (_, i) => ({
      id: i + 1,
      name: `Person ${i + 1}`,
    }));
    render(<ResultTable result={manyResults} />);

    expect(screen.getByText("5 строк")).toBeInTheDocument();
  });

  it("shows empty state when no results", () => {
    render(<ResultTable result={[]} />);

    expect(screen.getByText("Результатов не найдено")).toBeInTheDocument();
  });

  it("shows success message when results match and showDiff is true", () => {
    render(
      <ResultTable
        result={mockResult}
        expectedResult={mockExpectedResult}
        showDiff={true}
        success={true}
      />
    );

    expect(screen.getByText("Результат совпадает с ожидаемым")).toBeInTheDocument();
  });

  it("shows error message when results don't match and showDiff is true", () => {
    render(
      <ResultTable
        result={mockMismatchedResult}
        expectedResult={mockExpectedResult}
        showDiff={true}
        success={false}
      />
    );

    expect(screen.getByText("Результат не совпадает с ожидаемым")).toBeInTheDocument();
  });

  it("shows expected result table when results don't match", () => {
    render(
      <ResultTable
        result={mockMismatchedResult}
        expectedResult={mockExpectedResult}
        showDiff={true}
        success={false}
      />
    );

    expect(screen.getByText("Ожидаемый результат")).toBeInTheDocument();
  });

  it("highlights mismatched cells with warning emoji", () => {
    render(
      <ResultTable
        result={mockMismatchedResult}
        expectedResult={mockExpectedResult}
        showDiff={true}
        success={false}
      />
    );

    const cells = screen.getAllByText(/⚠️/);
    expect(cells.length).toBeGreaterThan(0);
  });

  it("renders NULL for null values", () => {
    const resultWithNull = [{ id: 1, name: "John", email: null }];
    render(<ResultTable result={resultWithNull} />);

    expect(screen.getByText("NULL")).toBeInTheDocument();
  });

  it("renders NULL for undefined values", () => {
    const resultWithUndefined = [{ id: 1, name: "John", email: undefined }];
    render(<ResultTable result={resultWithUndefined} />);

    expect(screen.getByText("NULL")).toBeInTheDocument();
  });

  it("doesn't show diff indicators when showDiff is false", () => {
    render(
      <ResultTable
        result={mockMismatchedResult}
        expectedResult={mockExpectedResult}
        showDiff={false}
        success={false}
      />
    );

    const cells = screen.queryAllByText(/⚠️/);
    expect(cells.length).toBe(0);
  });

  it("shows warning about extra rows", () => {
    const extraRows = [
      ...mockExpectedResult,
      { id: 3, name: "Extra Person", email: "extra@example.com" },
    ];

    render(
      <ResultTable
        result={extraRows}
        expectedResult={mockExpectedResult}
        showDiff={true}
        success={false}
      />
    );

    expect(screen.getByText(/Результат содержит 1 лишних строк/)).toBeInTheDocument();
  });

  it("shows warning about missing rows", () => {
    const fewerRows = [mockResult[0]];

    render(
      <ResultTable result={fewerRows} expectedResult={mockResult} showDiff={true} success={false} />
    );

    expect(screen.getByText(/Результату не хватает 1 строк/)).toBeInTheDocument();
  });
});
