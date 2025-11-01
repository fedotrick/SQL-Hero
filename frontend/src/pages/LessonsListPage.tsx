import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { BookOpen, Lock, Clock, AlertCircle, ArrowLeft } from "lucide-react";
import { LoadingScreen } from "../components/LoadingScreen";
import { Card, CardContent, Button, Badge } from "../components/ui";
import { coursesService } from "../services/courses";
import { useAuthStore } from "../store/authStore";
import type { ModuleDetail, LessonSummary } from "../types/courses";
import { telegramHaptics } from "../services/telegramHaptics";

export const LessonsListPage = () => {
  const { moduleId } = useParams<{ moduleId: string }>();
  const navigate = useNavigate();
  const { token } = useAuthStore();
  const [module, setModule] = useState<ModuleDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadModule = async () => {
      if (!token || !moduleId) {
        setError("Не авторизован или неверный ID модуля");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const moduleData = await coursesService.getModuleDetail(token, parseInt(moduleId));
        setModule(moduleData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Ошибка загрузки модуля");
      } finally {
        setLoading(false);
      }
    };

    loadModule();
  }, [token, moduleId]);

  const handleLessonClick = (lesson: LessonSummary) => {
    if (lesson.is_locked) {
      telegramHaptics.error();
      return;
    }
    telegramHaptics.light();
    navigate(`/lessons/${lesson.id}`);
  };

  const handleBack = () => {
    navigate("/modules");
  };

  const getStatusBadge = (status: string | null) => {
    switch (status) {
      case "COMPLETED":
        return (
          <Badge variant="success" size="sm">
            ✅ Завершено
          </Badge>
        );
      case "IN_PROGRESS":
        return (
          <Badge variant="info" size="sm">
            🟡 В процессе
          </Badge>
        );
      case "NOT_STARTED":
        return (
          <Badge variant="default" size="sm">
            ➡️ Не начато
          </Badge>
        );
      default:
        return null;
    }
  };

  if (loading) {
    return <LoadingScreen />;
  }

  if (error || !module) {
    return (
      <div className="min-h-screen bg-telegram-bg pb-20 px-4 pt-6">
        <Card variant="elevated" className="max-w-telegram mx-auto">
          <CardContent>
            <div className="text-center py-8">
              <AlertCircle className="mx-auto mb-4 text-telegram-destructive-text" size={48} />
              <h2 className="text-xl font-semibold text-telegram-text mb-2">Ошибка</h2>
              <p className="text-telegram-subtitle">{error || "Модуль не найден"}</p>
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
      <div className="max-w-telegram mx-auto p-4 space-y-6">
        <div className="flex items-center gap-3 mb-4">
          <Button variant="outline" size="sm" onClick={handleBack}>
            <ArrowLeft size={16} />
          </Button>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-telegram-text">{module.title}</h1>
            {module.description && (
              <p className="text-sm text-telegram-subtitle mt-1">{module.description}</p>
            )}
          </div>
        </div>

        <Card variant="elevated">
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <BookOpen className="text-telegram-button" size={24} />
                <div>
                  <p className="text-sm text-telegram-hint">Всего уроков</p>
                  <p className="text-xl font-bold text-telegram-text">{module.lessons.length}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-telegram-text">Уроки:</h2>
          {module.lessons.map((lesson) => (
            <Card
              key={lesson.id}
              interactive={!lesson.is_locked}
              className={`${lesson.is_locked ? "opacity-60" : ""}`}
              onClick={() => handleLessonClick(lesson)}
            >
              <CardContent>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-telegram-hint text-sm font-medium">
                        Урок {lesson.order}
                      </span>
                      {lesson.is_locked && <Lock size={16} className="text-telegram-hint" />}
                    </div>
                    <h3 className="text-base font-semibold text-telegram-text mb-1">
                      {lesson.title}
                    </h3>
                    {lesson.estimated_duration && (
                      <div className="flex items-center gap-1 text-sm text-telegram-subtitle">
                        <Clock size={14} />
                        <span>{lesson.estimated_duration} мин</span>
                      </div>
                    )}
                  </div>
                  <div className="flex-shrink-0">{getStatusBadge(lesson.progress_status)}</div>
                </div>
                {lesson.is_locked && (
                  <div className="text-xs text-telegram-hint bg-telegram-bg/50 rounded p-2 mt-3">
                    🔒 Завершите предыдущий урок, чтобы разблокировать
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};
