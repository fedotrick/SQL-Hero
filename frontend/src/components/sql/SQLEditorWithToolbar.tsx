import { useRef } from "react";
import { SQLEditor, type SQLEditorHandle } from "./SQLEditor";
import { MobileSQLToolbar } from "./MobileSQLToolbar";
import { useIsMobile } from "../../hooks/useSQLEditor";

interface SQLEditorWithToolbarProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  height?: string;
  tableNames?: string[];
  showToolbar?: boolean;
}

export const SQLEditorWithToolbar = ({
  value,
  onChange,
  disabled = false,
  height = "200px",
  tableNames = [],
  showToolbar = true,
}: SQLEditorWithToolbarProps) => {
  const isMobile = useIsMobile();
  const editorRef = useRef<SQLEditorHandle>(null);

  const handleInsert = (text: string) => {
    if (editorRef.current) {
      editorRef.current.insertText(text);
    } else {
      // Fallback: just append to the end
      onChange(value + text);
    }
  };

  return (
    <div className="space-y-0">
      <SQLEditor
        ref={editorRef}
        value={value}
        onChange={onChange}
        disabled={disabled}
        height={height}
        tableNames={tableNames}
      />
      {showToolbar && isMobile && <MobileSQLToolbar onInsert={handleInsert} disabled={disabled} />}
    </div>
  );
};
