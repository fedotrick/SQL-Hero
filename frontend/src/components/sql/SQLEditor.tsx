import { useRef, useEffect, forwardRef, useImperativeHandle } from "react";
import Editor, { type OnMount } from "@monaco-editor/react";
import type { editor, languages } from "monaco-editor";

export interface SQLEditorHandle {
  getEditor: () => editor.IStandaloneCodeEditor | null;
  insertText: (text: string) => void;
}

interface SQLEditorProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  height?: string;
  tableNames?: string[];
  readOnly?: boolean;
}

const SQL_KEYWORDS = [
  "SELECT",
  "FROM",
  "WHERE",
  "JOIN",
  "INNER JOIN",
  "LEFT JOIN",
  "RIGHT JOIN",
  "OUTER JOIN",
  "ON",
  "AND",
  "OR",
  "NOT",
  "IN",
  "LIKE",
  "BETWEEN",
  "IS NULL",
  "IS NOT NULL",
  "ORDER BY",
  "GROUP BY",
  "HAVING",
  "LIMIT",
  "OFFSET",
  "INSERT INTO",
  "UPDATE",
  "DELETE FROM",
  "CREATE TABLE",
  "DROP TABLE",
  "ALTER TABLE",
  "ASC",
  "DESC",
  "COUNT",
  "SUM",
  "AVG",
  "MIN",
  "MAX",
  "DISTINCT",
  "AS",
  "CASE",
  "WHEN",
  "THEN",
  "ELSE",
  "END",
];

export const SQLEditor = forwardRef<SQLEditorHandle, SQLEditorProps>(
  (
    { value, onChange, disabled = false, height = "200px", tableNames = [], readOnly = false },
    ref
  ) => {
    const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

    useImperativeHandle(ref, () => ({
      getEditor: () => editorRef.current,
      insertText: (text: string) => {
        const editor = editorRef.current;
        if (editor) {
          const selection = editor.getSelection();
          const position = selection ? selection.getStartPosition() : editor.getPosition();

          if (position) {
            editor.executeEdits("insert", [
              {
                range: {
                  startLineNumber: position.lineNumber,
                  startColumn: position.column,
                  endLineNumber: position.lineNumber,
                  endColumn: position.column,
                },
                text,
              },
            ]);

            const newPosition = {
              lineNumber: position.lineNumber,
              column: position.column + text.length,
            };
            editor.setPosition(newPosition);
            editor.focus();
          }
        }
      },
    }));

    const handleEditorDidMount: OnMount = (editor, monaco) => {
      editorRef.current = editor;

      // Configure SQL language completions
      monaco.languages.registerCompletionItemProvider("sql", {
        provideCompletionItems: (model, position) => {
          const word = model.getWordUntilPosition(position);
          const range = {
            startLineNumber: position.lineNumber,
            endLineNumber: position.lineNumber,
            startColumn: word.startColumn,
            endColumn: word.endColumn,
          };

          const suggestions: languages.CompletionItem[] = [];

          // Add SQL keywords
          SQL_KEYWORDS.forEach((keyword) => {
            suggestions.push({
              label: keyword,
              kind: monaco.languages.CompletionItemKind.Keyword,
              insertText: keyword,
              range,
              documentation: `SQL keyword: ${keyword}`,
            });
          });

          // Add table names
          tableNames.forEach((tableName) => {
            suggestions.push({
              label: tableName,
              kind: monaco.languages.CompletionItemKind.Class,
              insertText: tableName,
              range,
              documentation: `Table: ${tableName}`,
            });
          });

          return { suggestions };
        },
      });

      // Configure editor options
      editor.updateOptions({
        fontSize: 14,
        lineNumbers: "on",
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        wordWrap: "on",
        automaticLayout: true,
        readOnly: readOnly || disabled,
        tabSize: 2,
        insertSpaces: true,
        formatOnPaste: true,
        formatOnType: true,
      });
    };

    const handleEditorChange = (value: string | undefined) => {
      onChange(value || "");
    };

    // Update editor read-only state when disabled changes
    useEffect(() => {
      if (editorRef.current) {
        editorRef.current.updateOptions({
          readOnly: readOnly || disabled,
        });
      }
    }, [disabled, readOnly]);

    return (
      <div className="border border-telegram-hint/20 rounded-lg overflow-hidden">
        <Editor
          height={height}
          defaultLanguage="sql"
          value={value}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
          theme="vs-dark"
          options={{
            fontSize: 14,
            lineNumbers: "on",
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            wordWrap: "on",
            automaticLayout: true,
            readOnly: readOnly || disabled,
            tabSize: 2,
            insertSpaces: true,
          }}
        />
      </div>
    );
  }
);

SQLEditor.displayName = "SQLEditor";
