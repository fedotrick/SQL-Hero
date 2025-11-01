import { Button } from "../ui";

interface MobileSQLToolbarProps {
  onInsert: (text: string) => void;
  disabled?: boolean;
}

const SQL_SHORTCUTS = [
  { label: "SELECT", text: "SELECT " },
  { label: "FROM", text: "FROM " },
  { label: "WHERE", text: "WHERE " },
  { label: "JOIN", text: "JOIN " },
  { label: "AND", text: "AND " },
  { label: "OR", text: "OR " },
  { label: "ORDER BY", text: "ORDER BY " },
  { label: "LIMIT", text: "LIMIT " },
  { label: "*", text: "* " },
  { label: "=", text: "= " },
  { label: "LIKE", text: "LIKE " },
  { label: "IN", text: "IN " },
];

export const MobileSQLToolbar = ({ onInsert, disabled = false }: MobileSQLToolbarProps) => {
  return (
    <div
      className="bg-telegram-secondary-bg border-t border-telegram-hint/10 p-2 overflow-x-auto"
      data-testid="mobile-sql-toolbar"
    >
      <div className="flex gap-2 min-w-max">
        {SQL_SHORTCUTS.map((shortcut) => (
          <Button
            key={shortcut.label}
            variant="outline"
            size="sm"
            onClick={() => onInsert(shortcut.text)}
            disabled={disabled}
            className="whitespace-nowrap text-xs px-2 py-1"
            data-testid={`sql-toolbar-${shortcut.label.toLowerCase().replace(/\s+/g, "-")}`}
          >
            {shortcut.label}
          </Button>
        ))}
      </div>
    </div>
  );
};
