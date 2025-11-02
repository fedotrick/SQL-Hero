export interface ActivityHeatmapEntry {
  date: string;
  count: number;
}

export interface ActivityHeatmapResponse {
  user_id: number;
  start_date: string;
  end_date: string;
  data: ActivityHeatmapEntry[];
  total_activities: number;
}

export interface StreakData {
  current_streak: number;
  longest_streak: number;
  total_active_days: number;
  last_active_date: string | null;
  streak_start_date: string | null;
}

export interface ActivityCalendarResponse {
  heatmap: ActivityHeatmapResponse;
  streak: StreakData;
}

export interface DailyActivityStats {
  date: string;
  total_count: number;
  activity_by_type: Record<string, number>;
}
