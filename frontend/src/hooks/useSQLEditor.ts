import { useState, useCallback, useRef, useEffect } from "react";

export const useSQLEditor = (initialValue = "") => {
  const [value, setValue] = useState(initialValue);
  const [cursorPosition, setCursorPosition] = useState(0);
  const editorRef = useRef<HTMLTextAreaElement | null>(null);

  const insertText = useCallback(
    (text: string) => {
      setValue((prevValue) => {
        const beforeCursor = prevValue.slice(0, cursorPosition);
        const afterCursor = prevValue.slice(cursorPosition);
        const newValue = beforeCursor + text + afterCursor;

        // Update cursor position after insertion
        setTimeout(() => {
          setCursorPosition(beforeCursor.length + text.length);
        }, 0);

        return newValue;
      });
    },
    [cursorPosition]
  );

  const updateCursorPosition = useCallback((position: number) => {
    setCursorPosition(position);
  }, []);

  const reset = useCallback(() => {
    setValue(initialValue);
    setCursorPosition(0);
  }, [initialValue]);

  return {
    value,
    setValue,
    insertText,
    cursorPosition,
    updateCursorPosition,
    reset,
    editorRef,
  };
};

export const useIsMobile = (): boolean => {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener("resize", checkMobile);

    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  return isMobile;
};
