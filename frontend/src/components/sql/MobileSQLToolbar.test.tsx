import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MobileSQLToolbar } from "./MobileSQLToolbar";

describe("MobileSQLToolbar", () => {
  it("renders all SQL shortcut buttons", () => {
    const onInsert = vi.fn();
    render(<MobileSQLToolbar onInsert={onInsert} />);

    expect(screen.getByTestId("sql-toolbar-select")).toBeInTheDocument();
    expect(screen.getByTestId("sql-toolbar-from")).toBeInTheDocument();
    expect(screen.getByTestId("sql-toolbar-where")).toBeInTheDocument();
    expect(screen.getByTestId("sql-toolbar-join")).toBeInTheDocument();
    expect(screen.getByTestId("sql-toolbar-and")).toBeInTheDocument();
    expect(screen.getByTestId("sql-toolbar-or")).toBeInTheDocument();
    expect(screen.getByTestId("sql-toolbar-order-by")).toBeInTheDocument();
    expect(screen.getByTestId("sql-toolbar-limit")).toBeInTheDocument();
    expect(screen.getByTestId("sql-toolbar-*")).toBeInTheDocument();
    expect(screen.getByTestId("sql-toolbar-=")).toBeInTheDocument();
    expect(screen.getByTestId("sql-toolbar-like")).toBeInTheDocument();
    expect(screen.getByTestId("sql-toolbar-in")).toBeInTheDocument();
  });

  it("calls onInsert with correct text when SELECT button is clicked", async () => {
    const onInsert = vi.fn();
    const user = userEvent.setup();
    render(<MobileSQLToolbar onInsert={onInsert} />);

    const selectButton = screen.getByTestId("sql-toolbar-select");
    await user.click(selectButton);

    expect(onInsert).toHaveBeenCalledWith("SELECT ");
    expect(onInsert).toHaveBeenCalledTimes(1);
  });

  it("calls onInsert with correct text when FROM button is clicked", async () => {
    const onInsert = vi.fn();
    const user = userEvent.setup();
    render(<MobileSQLToolbar onInsert={onInsert} />);

    const fromButton = screen.getByTestId("sql-toolbar-from");
    await user.click(fromButton);

    expect(onInsert).toHaveBeenCalledWith("FROM ");
    expect(onInsert).toHaveBeenCalledTimes(1);
  });

  it("calls onInsert with correct text when WHERE button is clicked", async () => {
    const onInsert = vi.fn();
    const user = userEvent.setup();
    render(<MobileSQLToolbar onInsert={onInsert} />);

    const whereButton = screen.getByTestId("sql-toolbar-where");
    await user.click(whereButton);

    expect(onInsert).toHaveBeenCalledWith("WHERE ");
    expect(onInsert).toHaveBeenCalledTimes(1);
  });

  it("calls onInsert with correct text when JOIN button is clicked", async () => {
    const onInsert = vi.fn();
    const user = userEvent.setup();
    render(<MobileSQLToolbar onInsert={onInsert} />);

    const joinButton = screen.getByTestId("sql-toolbar-join");
    await user.click(joinButton);

    expect(onInsert).toHaveBeenCalledWith("JOIN ");
    expect(onInsert).toHaveBeenCalledTimes(1);
  });

  it("calls onInsert with correct text when ORDER BY button is clicked", async () => {
    const onInsert = vi.fn();
    const user = userEvent.setup();
    render(<MobileSQLToolbar onInsert={onInsert} />);

    const orderByButton = screen.getByTestId("sql-toolbar-order-by");
    await user.click(orderByButton);

    expect(onInsert).toHaveBeenCalledWith("ORDER BY ");
    expect(onInsert).toHaveBeenCalledTimes(1);
  });

  it("calls onInsert multiple times for multiple clicks", async () => {
    const onInsert = vi.fn();
    const user = userEvent.setup();
    render(<MobileSQLToolbar onInsert={onInsert} />);

    await user.click(screen.getByTestId("sql-toolbar-select"));
    await user.click(screen.getByTestId("sql-toolbar-*"));
    await user.click(screen.getByTestId("sql-toolbar-from"));

    expect(onInsert).toHaveBeenCalledTimes(3);
    expect(onInsert).toHaveBeenNthCalledWith(1, "SELECT ");
    expect(onInsert).toHaveBeenNthCalledWith(2, "* ");
    expect(onInsert).toHaveBeenNthCalledWith(3, "FROM ");
  });

  it("disables all buttons when disabled prop is true", () => {
    const onInsert = vi.fn();
    render(<MobileSQLToolbar onInsert={onInsert} disabled={true} />);

    const selectButton = screen.getByTestId("sql-toolbar-select");
    const fromButton = screen.getByTestId("sql-toolbar-from");
    const whereButton = screen.getByTestId("sql-toolbar-where");

    expect(selectButton).toBeDisabled();
    expect(fromButton).toBeDisabled();
    expect(whereButton).toBeDisabled();
  });

  it("does not call onInsert when buttons are disabled", async () => {
    const onInsert = vi.fn();
    const user = userEvent.setup();
    render(<MobileSQLToolbar onInsert={onInsert} disabled={true} />);

    const selectButton = screen.getByTestId("sql-toolbar-select");
    await user.click(selectButton);

    expect(onInsert).not.toHaveBeenCalled();
  });

  it("renders toolbar container with correct test id", () => {
    const onInsert = vi.fn();
    render(<MobileSQLToolbar onInsert={onInsert} />);

    expect(screen.getByTestId("mobile-sql-toolbar")).toBeInTheDocument();
  });
});
