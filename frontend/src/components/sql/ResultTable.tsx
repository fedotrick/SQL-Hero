import { CheckCircle, XCircle, AlertTriangle } from "lucide-react";
import { Card, CardContent } from "../ui";

type QueryResultRow = Record<string, unknown>;

interface ResultTableProps {
  result: QueryResultRow[];
  expectedResult?: QueryResultRow[];
  showDiff?: boolean;
  success?: boolean;
}

export const ResultTable = ({
  result,
  expectedResult,
  showDiff = false,
  success,
}: ResultTableProps) => {
  if (!result || result.length === 0) {
    return (
      <Card variant="elevated" className="mt-4">
        <CardContent>
          <div className="text-center py-8 text-telegram-subtitle">
            <AlertTriangle className="mx-auto mb-2" size={32} />
            <p>Результатов не найдено</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const columns = Object.keys(result[0]);
  const expectedColumns =
    expectedResult && expectedResult.length > 0 ? Object.keys(expectedResult[0]) : [];

  const isCellMatch = (rowIndex: number, colKey: string): boolean => {
    if (!showDiff || !expectedResult || expectedResult.length === 0) {
      return true;
    }
    if (rowIndex >= expectedResult.length) {
      return false;
    }
    const expectedRow = expectedResult[rowIndex];
    if (!(colKey in expectedRow)) {
      return false;
    }
    return result[rowIndex][colKey] === expectedRow[colKey];
  };

  const isRowMatch = (rowIndex: number): boolean => {
    if (!showDiff || !expectedResult || expectedResult.length === 0) {
      return true;
    }
    if (rowIndex >= expectedResult.length) {
      return false;
    }
    const resultRow = result[rowIndex];
    const expectedRow = expectedResult[rowIndex];
    return columns.every((col) => resultRow[col] === expectedRow[col]);
  };

  const hasExtraRows = result.length > (expectedResult?.length || 0);
  const hasMissingRows = (expectedResult?.length || 0) > result.length;

  return (
    <div className="space-y-4">
      {showDiff && expectedResult && (
        <div className="flex items-center gap-2 px-4">
          {success ? (
            <div className="flex items-center gap-2 text-green-500">
              <CheckCircle size={20} />
              <span className="text-sm font-medium">Результат совпадает с ожидаемым</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-red-500">
              <XCircle size={20} />
              <span className="text-sm font-medium">Результат не совпадает с ожидаемым</span>
            </div>
          )}
        </div>
      )}

      <Card variant="elevated">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-telegram-secondary-bg border-b border-telegram-hint/10">
                <tr>
                  {showDiff && (
                    <th className="px-3 py-2 text-left text-xs font-medium text-telegram-subtitle">
                      #
                    </th>
                  )}
                  {columns.map((col) => {
                    const isColumnMatch = !showDiff || expectedColumns.includes(col);
                    return (
                      <th
                        key={col}
                        className={`px-3 py-2 text-left text-xs font-medium ${
                          !isColumnMatch ? "text-red-500 bg-red-500/10" : "text-telegram-subtitle"
                        }`}
                      >
                        {col}
                        {!isColumnMatch && " ⚠️"}
                      </th>
                    );
                  })}
                </tr>
              </thead>
              <tbody>
                {result.map((row, rowIndex) => {
                  const rowMatch = isRowMatch(rowIndex);
                  return (
                    <tr
                      key={rowIndex}
                      className={`border-b border-telegram-hint/10 ${
                        !rowMatch && showDiff ? "bg-red-500/5" : "hover:bg-telegram-secondary-bg/50"
                      }`}
                    >
                      {showDiff && (
                        <td className="px-3 py-2 text-telegram-subtitle text-xs">
                          {rowMatch ? "✓" : "✗"}
                        </td>
                      )}
                      {columns.map((col) => {
                        const cellMatch = isCellMatch(rowIndex, col);
                        return (
                          <td
                            key={col}
                            className={`px-3 py-2 ${
                              !cellMatch && showDiff
                                ? "text-red-500 bg-red-500/10"
                                : "text-telegram-text"
                            }`}
                          >
                            {row[col] !== null && row[col] !== undefined
                              ? String(row[col])
                              : "NULL"}
                            {!cellMatch && showDiff && " ⚠️"}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {showDiff && (hasExtraRows || hasMissingRows) && (
            <div className="px-4 py-3 bg-yellow-500/10 border-t border-telegram-hint/10">
              <p className="text-sm text-yellow-600">
                {hasExtraRows &&
                  `Результат содержит ${result.length - (expectedResult?.length || 0)} лишних строк(и). `}
                {hasMissingRows &&
                  `Результату не хватает ${(expectedResult?.length || 0) - result.length} строк(и).`}
              </p>
            </div>
          )}
          <div className="px-4 py-2 bg-telegram-secondary-bg/50 border-t border-telegram-hint/10 text-xs text-telegram-subtitle">
            {result.length}{" "}
            {result.length === 1 ? "строка" : result.length < 5 ? "строки" : "строк"}
          </div>
        </CardContent>
      </Card>

      {showDiff && expectedResult && expectedResult.length > 0 && !success && (
        <Card variant="elevated">
          <CardContent>
            <h4 className="text-sm font-semibold text-telegram-text mb-3 flex items-center gap-2">
              <CheckCircle className="text-green-500" size={16} />
              Ожидаемый результат
            </h4>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-telegram-secondary-bg border-b border-telegram-hint/10">
                  <tr>
                    {expectedColumns.map((col) => (
                      <th
                        key={col}
                        className="px-3 py-2 text-left text-xs font-medium text-telegram-subtitle"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {expectedResult.map((row, rowIndex) => (
                    <tr
                      key={rowIndex}
                      className="border-b border-telegram-hint/10 hover:bg-telegram-secondary-bg/50"
                    >
                      {expectedColumns.map((col) => (
                        <td key={col} className="px-3 py-2 text-telegram-text">
                          {row[col] !== null && row[col] !== undefined ? String(row[col]) : "NULL"}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-2 text-xs text-telegram-subtitle">
              {expectedResult.length}{" "}
              {expectedResult.length === 1
                ? "строка"
                : expectedResult.length < 5
                  ? "строки"
                  : "строк"}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
