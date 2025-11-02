import { useState, useEffect } from "react";
import { Activity, Flame, Calendar, TrendingUp } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent, StreakCalendar, Skeleton } from "../components/ui";
import { activityService } from "../services";
import { ActivityCalendarResponse, DailyActivityStats } from "../types/activity";

export const StatsPage = () => {
  const [calendarData, setCalendarData] = useState<ActivityCalendarResponse | null>(null);
  const [selectedDayStats, setSelectedDayStats] = useState<DailyActivityStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const data = await activityService.getCalendarData();
        setCalendarData(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Не удалось загрузить данные");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleDayClick = async (date: string, count: number) => {
    if (count === 0) return;

    try {
      const stats = await activityService.getDailyStats(date);
      setSelectedDayStats(stats);
    } catch (err) {
      console.error("Failed to fetch daily stats:", err);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-telegram-bg pb-20">
        <div className="max-w-telegram mx-auto p-4 space-y-6">
          <header className="text-center py-6">
            <Activity className="mx-auto mb-3 text-telegram-button" size={48} />
            <h1 className="text-3xl font-bold text-telegram-text mb-2">Статистика активности</h1>
            <p className="text-telegram-subtitle">Ваши достижения и прогресс</p>
          </header>

          <Card>
            <CardContent className="p-6">
              <Skeleton className="h-48 w-full" />
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (error || !calendarData) {
    return (
      <div className="min-h-screen bg-telegram-bg pb-20">
        <div className="max-w-telegram mx-auto p-4 space-y-6">
          <Card variant="elevated">
            <CardContent className="p-6 text-center">
              <Activity className="mx-auto mb-3 text-telegram-destructive" size={48} />
              <h2 className="text-xl font-bold text-telegram-text mb-2">Ошибка загрузки</h2>
              <p className="text-telegram-subtitle">{error || "Не удалось загрузить данные"}</p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const { heatmap, streak } = calendarData;

  return (
    <div className="min-h-screen bg-telegram-bg pb-20">
      <div className="max-w-telegram mx-auto p-4 space-y-6">
        <header className="text-center py-6">
          <Activity className="mx-auto mb-3 text-telegram-button" size={48} />
          <h1 className="text-3xl font-bold text-telegram-text mb-2">Статистика активности</h1>
          <p className="text-telegram-subtitle">Ваши достижения и прогресс</p>
        </header>

        {/* Summary Stats */}
        <section>
          <h2 className="text-xl font-semibold text-telegram-text mb-4">Общая статистика</h2>
          <div className="grid grid-cols-2 gap-3">
            <Card>
              <CardContent className="p-4 text-center">
                <Flame className="mx-auto mb-2 text-orange-500" size={32} />
                <div className="text-2xl font-bold text-telegram-text">{streak.current_streak}</div>
                <div className="text-sm text-telegram-subtitle mt-1">Текущая серия</div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 text-center">
                <TrendingUp className="mx-auto mb-2 text-yellow-500" size={32} />
                <div className="text-2xl font-bold text-telegram-text">{streak.longest_streak}</div>
                <div className="text-sm text-telegram-subtitle mt-1">Лучшая серия</div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 text-center">
                <Calendar className="mx-auto mb-2 text-telegram-button" size={32} />
                <div className="text-2xl font-bold text-telegram-text">{streak.total_active_days}</div>
                <div className="text-sm text-telegram-subtitle mt-1">Активных дней</div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 text-center">
                <Activity className="mx-auto mb-2 text-purple-500" size={32} />
                <div className="text-2xl font-bold text-telegram-text">
                  {heatmap.total_activities}
                </div>
                <div className="text-sm text-telegram-subtitle mt-1">Всего активностей</div>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Activity Calendar */}
        <section>
          <Card>
            <CardHeader>
              <CardTitle>Календарь активности</CardTitle>
            </CardHeader>
            <CardContent>
              <StreakCalendar
                data={heatmap.data}
                startDate={heatmap.start_date}
                endDate={heatmap.end_date}
                currentStreak={streak.current_streak}
                longestStreak={streak.longest_streak}
                showLegend={true}
                animateNewStreak={streak.current_streak > 0}
                onDayClick={handleDayClick}
              />
            </CardContent>
          </Card>
        </section>

        {/* Selected Day Details */}
        {selectedDayStats && selectedDayStats.total_count > 0 && (
          <section>
            <Card variant="elevated">
              <CardHeader>
                <CardTitle>
                  Активность за{" "}
                  {new Date(selectedDayStats.date).toLocaleDateString("ru-RU", {
                    day: "numeric",
                    month: "long",
                    year: "numeric",
                  })}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-telegram-subtitle">Всего активностей:</span>
                    <span className="text-xl font-bold text-telegram-text">
                      {selectedDayStats.total_count}
                    </span>
                  </div>

                  {Object.keys(selectedDayStats.activity_by_type).length > 0 && (
                    <>
                      <div className="border-t border-telegram-separator pt-3">
                        <div className="text-sm font-semibold text-telegram-text mb-2">
                          По типам активности:
                        </div>
                        <div className="space-y-2">
                          {Object.entries(selectedDayStats.activity_by_type).map(([type, count]) => (
                            <div key={type} className="flex justify-between items-center">
                              <span className="text-sm text-telegram-subtitle capitalize">
                                {type.replace(/_/g, " ")}
                              </span>
                              <span className="text-sm font-semibold text-telegram-text">
                                {count}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          </section>
        )}

        {/* Last Active Date */}
        {streak.last_active_date && (
          <Card>
            <CardContent className="p-4">
              <div className="text-sm text-telegram-hint text-center">
                Последняя активность:{" "}
                <span className="text-telegram-text font-medium">
                  {new Date(streak.last_active_date).toLocaleDateString("ru-RU", {
                    day: "numeric",
                    month: "long",
                    year: "numeric",
                  })}
                </span>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};
