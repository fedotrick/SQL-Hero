/**
 * Extract table names from SQL content or theory text
 */
export const extractTableNames = (text: string): string[] => {
  const tableNames = new Set<string>();

  // Match common patterns for table mentions
  const patterns = [
    /FROM\s+`?(\w+)`?/gi,
    /JOIN\s+`?(\w+)`?/gi,
    /INTO\s+`?(\w+)`?/gi,
    /UPDATE\s+`?(\w+)`?/gi,
    /TABLE\s+`?(\w+)`?/gi,
    /таблиц[аеоуыэюя][йиюмей]*\s+`?(\w+)`?/gi, // Russian "таблица" and variations
  ];

  patterns.forEach((pattern) => {
    let match;
    while ((match = pattern.exec(text)) !== null) {
      if (match[1] && match[1].length > 0) {
        tableNames.add(match[1].toLowerCase());
      }
    }
  });

  return Array.from(tableNames);
};

/**
 * Format SQL query for display
 */
export const formatSQL = (sql: string): string => {
  return sql.replace(/\s+/g, " ").trim();
};

/**
 * Check if device is mobile based on screen width
 */
export const isMobileDevice = (): boolean => {
  return window.innerWidth < 768;
};
