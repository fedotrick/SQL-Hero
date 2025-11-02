import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { ActivityHeatmapEntry } from "../../types/activity";
import { Flame } from "lucide-react";

export interface StreakCalendarProps {
  data: ActivityHeatmapEntry[];
  startDate?: string;
  endDate?: string;
  currentStreak?: number;
  longestStreak?: number;
  showLegend?: boolean;
  animateNewStreak?: boolean;
  onDayClick?: (date: string, count: number) => void;
}

interface CalendarDay {
  date: string;
  count: number;
  weekIndex: number;
  dayIndex: number;
}

const DAYS_OF_WEEK = ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"];
const MONTHS = [
  "Янв",
  "Фев",
  "Мар",
  "Апр",
  "Май",
  "Июн",
  "Июл",
  "Авг",
  "Сен",
  "Окт",
  "Ноя",
  "Дек",
];

const getIntensityClass = (count: number, maxCount: number): string => {
  if (count === 0) return "bg-telegram-secondary-bg/30";

  const ratio = count / maxCount;
  if (ratio <= 0.25) return "bg-emerald-200 dark:bg-emerald-900/50";
  if (ratio <= 0.5) return "bg-emerald-300 dark:bg-emerald-700/60";
  if (ratio <= 0.75) return "bg-emerald-400 dark:bg-emerald-600/70";
  return "bg-emerald-500 dark:bg-emerald-500/80";
};

export const StreakCalendar: React.FC<StreakCalendarProps> = ({
  data,
  startDate,
  endDate,
  currentStreak = 0,
  longestStreak = 0,
  showLegend = true,
  animateNewStreak = false,
  onDayClick,
}) => {
  const [hoveredDay, setHoveredDay] = useState<CalendarDay | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });

  const { calendarData, maxCount, monthLabels } = useMemo(() => {
    // Create a map for quick lookup
    const dataMap = new Map(data.map((entry) => [entry.date, entry.count]));

    // Determine date range
    const end = endDate ? new Date(endDate) : new Date();
    const start = startDate ? new Date(startDate) : new Date(end.getTime() - 365 * 24 * 60 * 60 * 1000);

    // Get the first Sunday before or on the start date
    const firstDay = new Date(start);
    firstDay.setDate(firstDay.getDate() - firstDay.getDay());

    const days: CalendarDay[] = [];
    const monthLabels: Array<{ label: string; weekIndex: number }> = [];
    let currentMonth = -1;
    let weekIndex = 0;

    const current = new Date(firstDay);
    while (current <= end) {
      const dateStr = current.toISOString().split("T")[0];
      const count = dataMap.get(dateStr) || 0;
      const dayIndex = current.getDay();

      days.push({
        date: dateStr,
        count,
        weekIndex,
        dayIndex,
      });

      // Track month changes
      if (current.getMonth() !== currentMonth && dayIndex === 0) {
        currentMonth = current.getMonth();
        monthLabels.push({
          label: MONTHS[currentMonth],
          weekIndex,
        });
      }

      // Move to next day
      if (dayIndex === 6) {
        weekIndex++;
      }
      current.setDate(current.getDate() + 1);
    }

    const maxCount = Math.max(...data.map((d) => d.count), 1);

    return { calendarData: days, maxCount, monthLabels };
  }, [data, startDate, endDate]);

  const handleDayHover = (day: CalendarDay, event: React.MouseEvent) => {
    setHoveredDay(day);
    const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
    setTooltipPosition({
      x: rect.left + rect.width / 2,
      y: rect.top - 10,
    });
  };

  const handleDayClick = (day: CalendarDay) => {
    if (onDayClick) {
      onDayClick(day.date, day.count);
    }
  };

  const weeksCount = Math.max(...calendarData.map((d) => d.weekIndex)) + 1;

  return (
    <div className="space-y-4">
      {/* Streak Stats */}
      {(currentStreak > 0 || longestStreak > 0) && (
        <div className="flex gap-4 justify-center">
          {currentStreak > 0 && (
            <motion.div
              className="flex items-center gap-2 bg-telegram-secondary-bg px-4 py-2 rounded-lg"
              initial={animateNewStreak ? { scale: 0.8, opacity: 0 } : false}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ type: "spring", stiffness: 300, damping: 20 }}
            >
              <Flame className="text-orange-500" size={20} />
              <div>
                <div className="text-xs text-telegram-hint">Текущая серия</div>
                <div className="text-lg font-bold text-telegram-text">{currentStreak} дней</div>
              </div>
            </motion.div>
          )}
          {longestStreak > 0 && (
            <div className="flex items-center gap-2 bg-telegram-secondary-bg px-4 py-2 rounded-lg">
              <Flame className="text-yellow-500" size={20} />
              <div>
                <div className="text-xs text-telegram-hint">Лучшая серия</div>
                <div className="text-lg font-bold text-telegram-text">{longestStreak} дней</div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Calendar Grid */}
      <div className="relative overflow-x-auto">
        <div className="inline-block min-w-full">
          {/* Month labels */}
          <div className="flex mb-1" style={{ paddingLeft: "28px" }}>
            {monthLabels.map((month, index) => (
              <div
                key={index}
                className="text-xs text-telegram-hint"
                style={{
                  position: "absolute",
                  left: `${28 + month.weekIndex * 14}px`,
                }}
              >
                {month.label}
              </div>
            ))}
          </div>

          {/* Calendar */}
          <div className="flex gap-1">
            {/* Day labels */}
            <div className="flex flex-col gap-1 pr-2">
              {DAYS_OF_WEEK.map((day, index) => (
                <div
                  key={day}
                  className="text-xs text-telegram-hint h-3 leading-3"
                  style={{ visibility: index % 2 === 1 ? "visible" : "hidden" }}
                >
                  {day}
                </div>
              ))}
            </div>

            {/* Grid */}
            <div className="flex gap-1">
              {Array.from({ length: weeksCount }).map((_, weekIndex) => (
                <div key={weekIndex} className="flex flex-col gap-1">
                  {Array.from({ length: 7 }).map((_, dayIndex) => {
                    const day = calendarData.find(
                      (d) => d.weekIndex === weekIndex && d.dayIndex === dayIndex
                    );

                    if (!day) {
                      return <div key={dayIndex} className="w-3 h-3" />;
                    }

                    return (
                      <motion.div
                        key={`${weekIndex}-${dayIndex}`}
                        className={`w-3 h-3 rounded-sm cursor-pointer transition-transform hover:scale-125 ${getIntensityClass(day.count, maxCount)}`}
                        onMouseEnter={(e) => handleDayHover(day, e)}
                        onMouseLeave={() => setHoveredDay(null)}
                        onClick={() => handleDayClick(day)}
                        whileHover={{ scale: 1.25 }}
                        whileTap={{ scale: 0.95 }}
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{
                          delay: (weekIndex * 7 + dayIndex) * 0.001,
                          type: "spring",
                          stiffness: 500,
                          damping: 30,
                        }}
                      />
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Legend */}
      {showLegend && (
        <div className="flex items-center justify-end gap-2 text-xs text-telegram-hint">
          <span>Меньше</span>
          <div className="flex gap-1">
            <div className="w-3 h-3 rounded-sm bg-telegram-secondary-bg/30" />
            <div className="w-3 h-3 rounded-sm bg-emerald-200 dark:bg-emerald-900/50" />
            <div className="w-3 h-3 rounded-sm bg-emerald-300 dark:bg-emerald-700/60" />
            <div className="w-3 h-3 rounded-sm bg-emerald-400 dark:bg-emerald-600/70" />
            <div className="w-3 h-3 rounded-sm bg-emerald-500 dark:bg-emerald-500/80" />
          </div>
          <span>Больше</span>
        </div>
      )}

      {/* Tooltip */}
      {hoveredDay && (
        <motion.div
          className="fixed z-50 bg-telegram-text text-telegram-bg px-3 py-2 rounded-lg text-sm shadow-lg pointer-events-none"
          initial={{ opacity: 0, y: 0 }}
          animate={{ opacity: 1, y: -10 }}
          exit={{ opacity: 0 }}
          style={{
            left: tooltipPosition.x,
            top: tooltipPosition.y,
            transform: "translateX(-50%)",
          }}
        >
          <div className="font-semibold">
            {new Date(hoveredDay.date).toLocaleDateString("ru-RU", {
              day: "numeric",
              month: "long",
              year: "numeric",
            })}
          </div>
          <div className="text-xs opacity-90">
            {hoveredDay.count} {hoveredDay.count === 1 ? "активность" : "активностей"}
          </div>
        </motion.div>
      )}
    </div>
  );
};
