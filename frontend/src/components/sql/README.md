# SQL Editor Components

This directory contains components for SQL editing and result display, optimized for mobile and desktop use.

## Components

### SQLEditor

A Monaco-based code editor with SQL syntax highlighting, dark theme, and autocomplete.

**Features:**

- SQL syntax highlighting
- Dark theme (vs-dark)
- Autocomplete for SQL keywords
- Autocomplete for lesson-specific table names
- Configurable height
- Read-only and disabled states
- Exposed `insertText` method via ref

**Usage:**

```tsx
import { SQLEditor, SQLEditorHandle } from "./components/sql";

const editorRef = useRef<SQLEditorHandle>(null);

<SQLEditor
  ref={editorRef}
  value={query}
  onChange={setQuery}
  height="250px"
  tableNames={["users", "orders", "products"]}
  disabled={false}
/>;

// Insert text programmatically
editorRef.current?.insertText("SELECT * FROM ");
```

### MobileSQLToolbar

A horizontal scrollable toolbar with common SQL keywords for mobile users.

**Features:**

- Common SQL clauses (SELECT, FROM, WHERE, JOIN, etc.)
- Operators (=, \*, LIKE, IN)
- Horizontal scrolling on narrow screens
- Disabled state support

**Usage:**

```tsx
import { MobileSQLToolbar } from "./components/sql";

<MobileSQLToolbar onInsert={(text) => insertIntoEditor(text)} disabled={executing} />;
```

### SQLEditorWithToolbar

Combines SQLEditor with MobileSQLToolbar, automatically showing the toolbar on mobile devices.

**Features:**

- Auto-detects mobile screen width
- Intelligently inserts text at cursor position
- Manages editor instance internally
- Optional toolbar visibility

**Usage:**

```tsx
import { SQLEditorWithToolbar } from "./components/sql";

<SQLEditorWithToolbar
  value={query}
  onChange={setQuery}
  height="250px"
  tableNames={["users", "orders"]}
  showToolbar={true}
  disabled={false}
/>;
```

### ResultTable

Displays query results in a table with optional diff view for comparing with expected results.

**Features:**

- Responsive table layout
- NULL value handling
- Diff view with color-coded indicators
- Row count display
- Expected vs actual result comparison
- Warnings for extra/missing rows
- Column mismatch highlighting

**Usage:**

```tsx
import { ResultTable } from "./components/sql";

<ResultTable
  result={queryResults}
  expectedResult={lesson.expected_result}
  showDiff={!success}
  success={success}
/>;
```

## Utilities

### sqlHelpers

Helper functions for SQL-related operations:

- `extractTableNames(text: string): string[]` - Extracts table names from SQL text or lesson content
- `formatSQL(sql: string): string` - Formats SQL by removing extra whitespace
- `isMobileDevice(): boolean` - Checks if the current device is mobile

## Hooks

### useSQLEditor

Custom hook for managing SQL editor state:

```tsx
const { value, setValue, insertText, cursorPosition, updateCursorPosition, reset, editorRef } =
  useSQLEditor("");
```

### useIsMobile

Detects if the viewport is mobile-sized (width < 768px).

## Testing

All components have comprehensive test coverage:

- `MobileSQLToolbar.test.tsx` - Tests toolbar button actions
- `ResultTable.test.tsx` - Tests table rendering and diff view
- `SQLEditorWithToolbar.test.tsx` - Tests editor integration
- `sqlHelpers.test.ts` - Tests utility functions

Run tests with:

```bash
pnpm test
```

## Mobile Optimizations

- **Toolbar**: Shows on mobile to help with SQL keyword entry
- **Touch-friendly**: Large buttons and tap targets
- **Responsive**: Horizontal scrolling for toolbar on narrow screens
- **Editor**: Monaco's mobile-optimized touch gestures

## Dark Theme

All components use the Telegram theme colors for consistency:

- `telegram-bg` - Background
- `telegram-text` - Primary text
- `telegram-subtitle` - Secondary text
- `telegram-button` - Accent color
- `telegram-hint` - Muted text

## Performance

- Monaco Editor loads asynchronously
- Toolbar buttons use efficient event delegation
- Diff view only renders when needed
- Result tables use virtualization-friendly structure
