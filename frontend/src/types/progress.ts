export interface UserProgressSummary {
  user_id: number;
  username: string | null;
  xp: number;
  level: number;
  xp_to_next_level: number;
  current_level_xp: number;
  next_level_xp: number;
  progress_percentage: number;
  current_streak: number;
  longest_streak: number;
  total_queries: number;
  lessons_completed: number;
  total_lessons: number;
  modules_completed: number;
  total_modules: number;
  achievements_count: number;
  last_active_date: string | null;
}

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
