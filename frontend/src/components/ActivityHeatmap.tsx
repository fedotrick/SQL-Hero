import { motion } from "framer-motion";
import type { ActivityHeatmapEntry } from "../types/progress";

interface ActivityHeatmapProps {
  data: ActivityHeatmapEntry[];
  maxCount?: number;
}

export const ActivityHeatmap = ({ data, maxCount }: ActivityHeatmapProps) => {
  const max = maxCount || Math.max(...data.map((d) => d.count), 1);

  const getColor = (count: number) => {
    if (count === 0) return "bg-telegram-section-bg";
    const intensity = count / max;
    if (intensity < 0.25) return "bg-telegram-link/20";
    if (intensity < 0.5) return "bg-telegram-link/40";
    if (intensity < 0.75) return "bg-telegram-link/60";
    return "bg-telegram-link";
  };

  const recentData = data.slice(-84);

  const weeks: ActivityHeatmapEntry[][] = [];
  for (let i = 0; i < recentData.length; i += 7) {
    weeks.push(recentData.slice(i, i + 7));
  }

  return (
    <div className="overflow-x-auto">
      <div className="flex gap-1 min-w-min">
        {weeks.map((week, weekIndex) => (
          <div key={weekIndex} className="flex flex-col gap-1">
            {week.map((day, dayIndex) => (
              <motion.div
                key={`${weekIndex}-${dayIndex}`}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: (weekIndex * 7 + dayIndex) * 0.01 }}
                className={`w-3 h-3 rounded-sm ${getColor(day.count)}`}
                title={`${day.date}: ${day.count} ${day.count === 1 ? "activity" : "activities"}`}
              />
            ))}
          </div>
        ))}
      </div>
      <div className="flex items-center gap-2 mt-3 text-xs text-telegram-hint">
        <span>Less</span>
        <div className="flex gap-1">
          <div className="w-3 h-3 rounded-sm bg-telegram-section-bg" />
          <div className="w-3 h-3 rounded-sm bg-telegram-link/20" />
          <div className="w-3 h-3 rounded-sm bg-telegram-link/40" />
          <div className="w-3 h-3 rounded-sm bg-telegram-link/60" />
          <div className="w-3 h-3 rounded-sm bg-telegram-link" />
        </div>
        <span>More</span>
      </div>
    </div>
  );
};
