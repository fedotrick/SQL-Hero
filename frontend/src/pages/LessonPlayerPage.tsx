import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  BookOpen,
  Lock,
  Play,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  Award,
  Zap,
} from "lucide-react";
import { LoadingScreen } from "../components/LoadingScreen";
import { Card, CardContent, Button, Badge } from "../components/ui";
import { SQLEditorWithToolbar, ResultTable } from "../components/sql";
import { coursesService } from "../services/courses";
import { progressService } from "../services/progress";
import { useAuthStore } from "../store/authStore";
import type { LessonDetail } from "../types/courses";
import type { LessonAttemptResponse } from "../types/progress";
import { telegramHaptics } from "../services/telegramHaptics";
import { extractTableNames } from "../utils/sqlHelpers";

export const LessonPlayerPage = () => {
  const { lessonId } = useParams<{ lessonId: string }>();
  const navigate = useNavigate();
  const { token } = useAuthStore();
  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sqlQuery, setSqlQuery] = useState("");
  const [executing, setExecuting] = useState(false);
  const [result, setResult] = useState<LessonAttemptResponse | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [queryResult, setQueryResult] = useState<Record<string, unknown>[] | null>(null);

  useEffect(() => {
    const loadLesson = async () => {
      if (!token || !lessonId) {
        setError("Не авторизован или неверный ID урока");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const lessonData = await coursesService.getLessonDetail(token, parseInt(lessonId));
        setLesson(lessonData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Ошибка загрузки урока");
      } finally {
        setLoading(false);
      }
    };

    loadLesson();
  }, [token, lessonId]);

  const handleRunQuery = async () => {
    if (!lesson || !token || !sqlQuery.trim()) {
      return;
    }

    if (lesson.is_locked) {
      telegramHaptics.error();
      return;
    }

    try {
      setExecuting(true);
      setShowResult(false);
      setQueryResult(null);
      telegramHaptics.light();

      // For now, we'll do a simple check - in a real implementation,
      // this would execute the query in a sandbox and compare results
      const success = sqlQuery.trim().toLowerCase() === lesson.sql_solution?.toLowerCase().trim();

      // Mock query result for demonstration
      // In production, this would come from executing the query
      const mockResult = [
        { id: 1, name: "John Doe", email: "john@example.com" },
        { id: 2, name: "Jane Smith", email: "jane@example.com" },
      ];
      setQueryResult(mockResult);

      const attemptResult = await progressService.submitLessonAttempt(token, lesson.id, {
        user_query: sqlQuery,
        success,
      });

      setResult(attemptResult);
      setShowResult(true);

      if (attemptResult.success) {
        telegramHaptics.success();
      } else {
        telegramHaptics.error();
      }

      // Update lesson attempts
      setLesson({
        ...lesson,
        attempts: attemptResult.attempts,
        progress_status: attemptResult.progress_status,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка выполнения запроса");
      telegramHaptics.error();
    } finally {
      setExecuting(false);
    }
  };

  const handleBack = () => {
    if (lesson) {
      navigate(`/modules/${lesson.module_id}/lessons`);
    } else {
      navigate("/modules");
    }
  };

  const handleNextLesson = () => {
    // Navigate to next lesson (would need to fetch module lessons to determine)
    // For now, just go back to lessons list
    if (lesson) {
      navigate(`/modules/${lesson.module_id}/lessons`);
    }
  };

  const handlePrevLesson = () => {
    // Navigate to previous lesson (would need to fetch module lessons to determine)
    // For now, just go back to lessons list
    if (lesson) {
      navigate(`/modules/${lesson.module_id}/lessons`);
    }
  };

  if (loading) {
    return <LoadingScreen />;
  }

  if (error || !lesson) {
    return (
      <div className="min-h-screen bg-telegram-bg pb-20 px-4 pt-6">
        <Card variant="elevated" className="max-w-telegram mx-auto">
          <CardContent>
            <div className="text-center py-8">
              <AlertCircle className="mx-auto mb-4 text-telegram-destructive-text" size={48} />
              <h2 className="text-xl font-semibold text-telegram-text mb-2">Ошибка</h2>
              <p className="text-telegram-subtitle">{error || "Урок не найден"}</p>
              <Button className="mt-4" onClick={handleBack}>
                Вернуться
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (lesson.is_locked) {
    return (
      <div className="min-h-screen bg-telegram-bg pb-20 px-4 pt-6">
        <Card variant="elevated" className="max-w-telegram mx-auto">
          <CardContent>
            <div className="text-center py-8">
              <Lock className="mx-auto mb-4 text-telegram-hint" size={48} />
              <h2 className="text-xl font-semibold text-telegram-text mb-2">Урок заблокирован</h2>
              <p className="text-telegram-subtitle">
                Завершите предыдущий урок, чтобы разблокировать этот
              </p>
              <Button className="mt-4" onClick={handleBack}>
                Вернуться
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-telegram-bg pb-20">
      <div className="max-w-telegram mx-auto">
        {/* Header */}
        <div className="sticky top-0 bg-telegram-bg z-10 border-b border-telegram-hint/10 p-4">
          <div className="flex items-center justify-between mb-2">
            <Button variant="outline" size="sm" onClick={handleBack}>
              <ChevronLeft size={16} />
              <span className="ml-1">Назад</span>
            </Button>
            <div className="flex items-center gap-2">
              <Badge variant="info" size="sm">
                Попыток: {lesson.attempts}
              </Badge>
              {lesson.progress_status === "completed" && (
                <Badge variant="success" size="sm">
                  ✅ Завершено
                </Badge>
              )}
            </div>
          </div>
          <h1 className="text-xl font-bold text-telegram-text">{lesson.title}</h1>
        </div>

        {/* Theory Section */}
        <div className="p-4 space-y-4">
          {lesson.theory && (
            <Card variant="elevated">
              <CardContent>
                <div className="flex items-center gap-2 mb-3">
                  <BookOpen className="text-telegram-button" size={20} />
                  <h2 className="text-lg font-semibold text-telegram-text">Теория</h2>
                </div>
                <div className="prose prose-sm text-telegram-text whitespace-pre-wrap">
                  {lesson.theory}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Task Description */}
          {lesson.content && (
            <Card variant="elevated">
              <CardContent>
                <h3 className="text-base font-semibold text-telegram-text mb-2">Задание</h3>
                <p className="text-telegram-subtitle whitespace-pre-wrap">{lesson.content}</p>
              </CardContent>
            </Card>
          )}

          {/* SQL Editor */}
          <Card variant="elevated">
            <CardContent>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-base font-semibold text-telegram-text">SQL Редактор</h3>
              </div>
              <SQLEditorWithToolbar
                value={sqlQuery}
                onChange={setSqlQuery}
                disabled={executing}
                height="250px"
                tableNames={extractTableNames(
                  `${lesson.theory || ""} ${lesson.content || ""} ${lesson.sql_solution || ""}`
                )}
                showToolbar={true}
              />
              <Button
                className="w-full mt-3"
                onClick={handleRunQuery}
                disabled={executing || !sqlQuery.trim()}
              >
                {executing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                    Выполнение...
                  </>
                ) : (
                  <>
                    <Play size={16} className="mr-2" />
                    Запустить
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Query Results */}
          {queryResult && queryResult.length > 0 && (
            <ResultTable
              result={queryResult}
              expectedResult={
                lesson.expected_result && Array.isArray(lesson.expected_result)
                  ? lesson.expected_result
                  : undefined
              }
              showDiff={!result?.success}
              success={result?.success}
            />
          )}

          {/* Result Panel */}
          {showResult && result && (
            <Card
              variant="elevated"
              className={result.success ? "border-green-500/50" : "border-red-500/50"}
            >
              <CardContent>
                <div className="space-y-3">
                  <p className="text-telegram-subtitle text-sm">{result.message}</p>

                  {result.success && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm">
                        <Zap className="text-yellow-500" size={16} />
                        <span className="text-telegram-text">
                          +{result.xp_earned} XP
                          {result.first_try && " (первая попытка!)"}
                        </span>
                      </div>
                      {result.level_up && (
                        <div className="flex items-center gap-2 text-sm">
                          <Award className="text-purple-500" size={16} />
                          <span className="text-telegram-text">
                            Новый уровень: {result.level}! 🎊
                          </span>
                        </div>
                      )}
                      {result.achievements_unlocked.length > 0 && (
                        <div className="mt-3 p-3 bg-telegram-bg rounded-lg">
                          <p className="text-sm font-semibold text-telegram-text mb-2">
                            Разблокированы достижения:
                          </p>
                          {result.achievements_unlocked.map((achievement) => (
                            <div
                              key={achievement.achievement_id}
                              className="flex items-center gap-2 text-sm"
                            >
                              {achievement.icon && <span>{achievement.icon}</span>}
                              <span className="text-telegram-text">{achievement.title}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between gap-3 pt-4">
            <Button variant="outline" onClick={handlePrevLesson}>
              <ChevronLeft size={16} />
              Предыдущий
            </Button>
            <Button variant="outline" onClick={handleNextLesson}>
              Следующий
              <ChevronRight size={16} />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
