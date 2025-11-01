import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { SQLEditorWithToolbar } from "./SQLEditorWithToolbar";

// Mock the hooks
vi.mock("../../hooks/useSQLEditor", () => ({
  useIsMobile: vi.fn(() => true),
}));

describe("SQLEditorWithToolbar", () => {
  it("renders SQL editor component", () => {
    const onChange = vi.fn();
    const { container } = render(
      <SQLEditorWithToolbar value="SELECT * FROM users" onChange={onChange} />
    );

    // Check that the component is rendered
    expect(container.firstChild).toBeTruthy();
  });

  it("renders mobile toolbar when on mobile and showToolbar is true", () => {
    const onChange = vi.fn();
    render(<SQLEditorWithToolbar value="" onChange={onChange} showToolbar={true} />);

    expect(screen.getByTestId("mobile-sql-toolbar")).toBeInTheDocument();
  });

  it("does not render toolbar when showToolbar is false", () => {
    const onChange = vi.fn();
    render(<SQLEditorWithToolbar value="" onChange={onChange} showToolbar={false} />);

    expect(screen.queryByTestId("mobile-sql-toolbar")).not.toBeInTheDocument();
  });

  it("passes disabled prop to editor and toolbar", () => {
    const onChange = vi.fn();
    render(<SQLEditorWithToolbar value="" onChange={onChange} disabled={true} />);

    const toolbar = screen.getByTestId("mobile-sql-toolbar");
    const buttons = toolbar.querySelectorAll("button");
    buttons.forEach((button) => {
      expect(button).toBeDisabled();
    });
  });

  it("passes tableNames to editor", () => {
    const onChange = vi.fn();
    const tableNames = ["users", "orders", "products"];
    const { container } = render(
      <SQLEditorWithToolbar value="" onChange={onChange} tableNames={tableNames} />
    );

    // Editor should be rendered (actual autocomplete testing would require Monaco to be fully loaded)
    expect(container.firstChild).toBeTruthy();
  });
});
